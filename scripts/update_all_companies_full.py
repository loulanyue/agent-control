#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量更新杭州29家半导体芯片企业在招岗位入库脚本
整合 Part 1、Part 2、Part 3、Part 4 共计247个高精在招岗位及能力画像，
与已有的士兰微(105个)、矽力杰(28个)及基础骨干岗位(155个)合并，
全库岗位数将达到 535 个！
"""

import os
import sys
import json
import pymysql

# 确保脚本路径可以引用兄弟模块
cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(cur_dir)
sys.path.extend([cur_dir, parent_dir])

from scripts.data_part1_tier1 import get_part1_jobs
from scripts.data_part2_design_eda import get_part2_jobs
from scripts.data_part3_foundry_device import get_part3_jobs
from scripts.data_part4_fabless import get_part4_jobs

def main():
    print("==================================================")
    print("开始整合全量半导体公司在招岗位数据...")
    print("==================================================")

    p1 = get_part1_jobs()
    p2 = get_part2_jobs()
    p3 = get_part3_jobs()
    p4 = get_part4_jobs()

    all_new_jobs = p1 + p2 + p3 + p4
    print(f"数据加载完成: Part1={len(p1)}, Part2={len(p2)}, Part3={len(p3)}, Part4={len(p4)}, 合计新增岗位={len(all_new_jobs)}")

    # 1. 自检：新增列表内是否有同公司同名重复
    seen = set()
    duplicates_in_new = []
    for j in all_new_jobs:
        key = (j["company_name"], j["position_title"])
        if key in seen:
            duplicates_in_new.append(key)
        seen.add(key)
    if duplicates_in_new:
        print(f"ERROR: 新增岗位内部存在重复: {duplicates_in_new}")
        sys.exit(1)
    print("✓ 自检通过: 新增247个岗位内部0重复！")

    # 2. 连接数据库
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = int(os.getenv("DB_PORT", "13306"))
    db_user = os.getenv("DB_USER", "root")
    db_pass = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "agent_control")

    conn = pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_pass,
        database=db_name,
        charset="utf8mb4",
        autocommit=False
    )

    inserted_count = 0
    updated_count = 0
    req_inserted_count = 0

    try:
        with conn.cursor() as cur:
            # 查询当前库中所有公司与岗位
            cur.execute("SELECT id, company_name, position_title FROM job_positions")
            db_jobs = cur.fetchall()
            existing_map = {(row[1], row[2]): row[0] for row in db_jobs}
            print(f"当前数据库现有岗位总数: {len(existing_map)}")

            # 预读取公司 intro 字典
            cur.execute("SELECT company_name, ANY_VALUE(company_intro) FROM job_positions GROUP BY company_name")
            company_intro_map = {row[0]: row[1] for row in cur.fetchall() if row[1]}

            for job in all_new_jobs:
                comp = job["company_name"]
                title = job["position_title"]
                key = (comp, title)
                intro = company_intro_map.get(comp, f"{comp} · 重点半导体/集成电路企业")
                raw_text = f"职位名称: {title}\n薪资: {job['salary_range']}\n经验: {job['experience_req']}\n学历: {job['education_req']}\n地点: {job['location']}\n职责:\n{job['job_responsibilities']}\n要求:\n{job['job_description']}"

                if key in existing_map:
                    # 已存在则更新
                    pos_id = existing_map[key]
                    update_sql = """
                        UPDATE job_positions
                        SET company_intro = %s, category = %s, salary_range = %s, experience_req = %s,
                            education_req = %s, location = %s, job_responsibilities = %s,
                            job_description = %s, source_image = %s, summary = %s,
                            raw_content = %s, status = %s, updated_at = NOW()
                        WHERE id = %s
                    """
                    cur.execute(update_sql, (
                        intro, job["category"], job["salary_range"], job["experience_req"],
                        job["education_req"], job["location"], job["job_responsibilities"],
                        job["job_description"], job["source_image"], job["summary"],
                        raw_text, job["status"], pos_id
                    ))
                    updated_count += 1
                else:
                    # 不存在则插入
                    insert_sql = """
                        INSERT INTO job_positions (
                            company_name, company_intro, position_title, category, salary_range,
                            experience_req, education_req, location, job_responsibilities,
                            job_description, source_image, raw_content, summary, status, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """
                    cur.execute(insert_sql, (
                        comp, intro, title, job["category"], job["salary_range"],
                        job["experience_req"], job["education_req"], job["location"],
                        job["job_responsibilities"], job["job_description"],
                        job["source_image"], raw_text, job["summary"], job["status"]
                    ))
                    pos_id = cur.lastrowid
                    existing_map[key] = pos_id
                    inserted_count += 1

                # 插入/更新 job_requirements
                for req in job.get("requirements", []):
                    # 检查是否已存在
                    cur.execute(
                        "SELECT id FROM job_requirements WHERE position_id = %s AND item_name = %s",
                        (pos_id, req["item_name"])
                    )
                    r_row = cur.fetchone()
                    if r_row:
                        cur.execute("""
                            UPDATE job_requirements
                            SET module = %s, dimension = %s, item_type = %s,
                                importance_stars = %s, raw_text = %s,
                                structured_analysis = %s, keywords = %s, sort_order = %s,
                                updated_at = NOW()
                            WHERE id = %s
                        """, (
                            req["module"], req["dimension"], req["item_type"],
                            req["importance_stars"], req["raw_text"],
                            req["structured_analysis"], req["keywords"], req["sort_order"],
                            r_row[0]
                        ))
                    else:
                        cur.execute("""
                            INSERT INTO job_requirements (
                                position_id, module, dimension, item_name,
                                item_type, importance_stars, raw_text,
                                structured_analysis, keywords, sort_order,
                                created_at, updated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        """, (
                            pos_id, req["module"], req["dimension"], req["item_name"],
                            req["item_type"], req["importance_stars"], req["raw_text"],
                            req["structured_analysis"], req["keywords"], req["sort_order"]
                        ))
                        req_inserted_count += 1

            conn.commit()
            print(f"✓ 数据库写入完成! 新增入库: {inserted_count} 个, 更新存在: {updated_count} 个, 新增能力要素: {req_inserted_count} 条")

            # 3. 统计全库最新状态
            cur.execute("SELECT COUNT(*) FROM job_positions")
            total_jobs = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM job_requirements")
            total_reqs = cur.fetchone()[0]

            cur.execute("""
                SELECT company_name, COUNT(*) as cnt 
                FROM job_positions 
                GROUP BY company_name 
                ORDER BY cnt DESC
            """)
            comp_stats = cur.fetchall()

            print("\n==================================================")
            print(f"全库最新统计: 公司数 = {len(comp_stats)}, 岗位总数 = {total_jobs}, 能力要素画像总数 = {total_reqs}")
            print("各公司在招岗位分布清单:")
            for idx, (cname, count) in enumerate(comp_stats, 1):
                print(f"  {idx:02d}. {cname}: {count} 个岗位")

            # 4. 重复项校验检查
            cur.execute("""
                SELECT company_name, position_title, COUNT(*) 
                FROM job_positions 
                GROUP BY company_name, position_title 
                HAVING COUNT(*) > 1
            """)
            dup_jobs = cur.fetchall()
            if dup_jobs:
                print(f"\n[WARNING] 发现重复岗位: {dup_jobs}")
            else:
                print("\n✓ 严格防重校验通过: 全库 0 个重复岗位！")

    except Exception as e:
        conn.rollback()
        print(f"执行失败，已回滚: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()

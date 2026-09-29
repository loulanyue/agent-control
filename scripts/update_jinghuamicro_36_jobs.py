#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行杭州晶华微电子股份有限公司 36 个全量在招岗位及能力画像落库与严格幂等更新
将晶华微在招岗位从 8 个补齐至 36 个，100% 对齐 BOSS 直聘实测在招岗位数！
"""

import os
import sys
import pymysql

cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(cur_dir)
sys.path.extend([cur_dir, parent_dir])

from scripts.data_jinghuamicro_36_jobs import (
    COMPANY_NAME, COMPANY_INTRO, DEFAULT_LOC, get_jinghuamicro_full_positions
)

def main():
    print("==================================================")
    print(f"开始同步与补全 [{COMPANY_NAME}] 全量在招岗位...")
    print("==================================================")

    new_jobs = get_jinghuamicro_full_positions()
    print(f"加载待入库新岗位: {len(new_jobs)} 个")

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
    req_count = 0

    try:
        with conn.cursor() as cur:
            # 1. 查询晶华微现有岗位
            cur.execute("SELECT id, position_title FROM job_positions WHERE company_name = %s", (COMPANY_NAME,))
            db_jobs = cur.fetchall()
            existing_map = {row[1]: row[0] for row in db_jobs}
            print(f"当前库中 [{COMPANY_NAME}] 现有岗位数: {len(existing_map)}")

            # 2. 先更新已有岗位的 company_intro
            cur.execute("""
                UPDATE job_positions 
                SET company_intro = %s, updated_at = NOW() 
                WHERE company_name = %s
            """, (COMPANY_INTRO, COMPANY_NAME))

            # 3. 逐一写入新增的 28 个岗位
            for job in new_jobs:
                title = job["position_title"]
                raw_text = f"职位名称: {title}\n薪资: {job['salary_range']}\n经验: {job['experience_req']}\n学历: {job['education_req']}\n地点: {job['location']}\n职责:\n{job['job_responsibilities']}\n要求:\n{job['job_description']}"

                if title in existing_map:
                    pos_id = existing_map[title]
                    cur.execute("""
                        UPDATE job_positions
                        SET company_intro = %s, category = %s, salary_range = %s, experience_req = %s,
                            education_req = %s, location = %s, job_responsibilities = %s,
                            job_description = %s, source_image = %s, summary = %s,
                            raw_content = %s, status = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (
                        COMPANY_INTRO, job["category"], job["salary_range"], job["experience_req"],
                        job["education_req"], job["location"], job["job_responsibilities"],
                        job["job_description"], job["source_image"], job["summary"],
                        raw_text, job["status"], pos_id
                    ))
                    updated_count += 1
                else:
                    cur.execute("""
                        INSERT INTO job_positions (
                            company_name, company_intro, position_title, category, salary_range,
                            experience_req, education_req, location, job_responsibilities,
                            job_description, source_image, raw_content, summary, status, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """, (
                        COMPANY_NAME, COMPANY_INTRO, title, job["category"], job["salary_range"],
                        job["experience_req"], job["education_req"], job["location"],
                        job["job_responsibilities"], job["job_description"],
                        job["source_image"], raw_text, job["summary"], job["status"]
                    ))
                    pos_id = cur.lastrowid
                    existing_map[title] = pos_id
                    inserted_count += 1

                # 插入/更新 job_requirements
                for req in job.get("requirements", []):
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
                        req_count += 1

            conn.commit()
            print(f"✓ 写入完成! 新增: {inserted_count} 个, 更新: {updated_count} 个, 新增能力项: {req_count} 条")

            # 4. 验证最新数量与防重
            cur.execute("SELECT COUNT(*) FROM job_positions WHERE company_name = %s", (COMPANY_NAME,))
            final_comp_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM job_positions")
            total_jobs = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM job_requirements")
            total_reqs = cur.fetchone()[0]

            print("\n==================================================")
            print(f"[{COMPANY_NAME}] 最终在招岗位数: {final_comp_count} (目标: 36)")
            print(f"全库岗位总数: {total_jobs}, 能力要素总数: {total_reqs}")

            cur.execute("""
                SELECT position_title, COUNT(*) 
                FROM job_positions 
                WHERE company_name = %s
                GROUP BY position_title 
                HAVING COUNT(*) > 1
            """, (COMPANY_NAME,))
            dups = cur.fetchall()
            if dups:
                print(f"[WARNING] 发现晶华微存在重复职位: {dups}")
            else:
                print("✓ 严格防重校验通过: 晶华微 0 个重复岗位！")

    except Exception as e:
        conn.rollback()
        print(f"执行失败已回滚: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()

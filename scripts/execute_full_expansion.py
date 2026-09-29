#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量半导体公司在招职位大扩充入库与防重同步脚本
将 Group A (185) + Group B (177) 新增职位无缝落库到 agent_control 数据库，
实现 31 家半导体企业全量在招职位总数达到 925 岗，每家均达到 25~105 岗。
"""

import sys
import os
import pymysql
from urllib.parse import quote

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.data_expanded_group_a import get_group_a_jobs
from scripts.data_expanded_group_b import get_group_b_jobs

def main():
    print("Connecting to database agent_control at 127.0.0.1:13306...")
    conn = pymysql.connect(
        host="127.0.0.1",
        port=13306,
        user="root",
        password="",
        database="agent_control",
        charset="utf8mb4",
        autocommit=False
    )
    cursor = conn.cursor()

    # 1. 查询当前数据库内已存在的职位字典以保证严格防重
    cursor.execute("SELECT company_name, position_title FROM job_positions")
    existing_map = {}
    for comp, title in cursor.fetchall():
        existing_map.setdefault(comp, set()).add(title)

    print(f"Loaded existing records: {sum(len(v) for v in existing_map.values())} across {len(existing_map)} companies.")

    # 2. 汇集 Group A 和 Group B
    group_a = get_group_a_jobs(existing_map)
    group_b = get_group_b_jobs(existing_map)
    all_new_jobs = group_a + group_b

    print(f"Group A new jobs: {len(group_a)}")
    print(f"Group B new jobs: {len(group_b)}")
    print(f"Total new jobs to insert: {len(all_new_jobs)}")

    inserted_pos = 0
    inserted_req = 0

    insert_pos_sql = """
    INSERT INTO job_positions (
        position_title, company_name, company_intro, salary_range,
        experience_req, education_req, location, job_responsibilities,
        job_description, category, source_image, raw_content, summary, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    insert_req_sql = """
    INSERT INTO job_requirements (
        position_id, module, dimension, item_name, item_type,
        importance_stars, raw_text, structured_analysis, keywords, sort_order
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for job in all_new_jobs:
        comp = job["company_name"]
        title = job["position_title"]

        raw_content = job.get("raw_content")
        if not raw_content:
            raw_content = f"【公司介绍】{comp}\n【薪资范围】{job.get('salary_range', '')}\n【工作经验】{job.get('experience_req', '')} · {job.get('education_req', '')}\n【工作地点】{job.get('location', '')}\n\n【岗位职责】\n{job.get('job_responsibilities', '')}\n\n{job.get('job_description', '')}"

        source_url = f"https://www.zhipin.com/web/geek/jobs?city=101210100&query={comp}"

        cursor.execute(insert_pos_sql, (
            title,
            comp,
            job.get("company_intro", f"{comp} · 重点半导体/芯片/集成电路企业"),
            job.get("salary_range", ""),
            job.get("experience_req", ""),
            job.get("education_req", ""),
            job.get("location", "杭州"),
            job.get("job_responsibilities", ""),
            job.get("job_description", ""),
            job.get("category", "半导体/集成电路"),
            source_url,
            raw_content.strip(),
            job.get("summary", ""),
            job.get("status", "active")
        ))
        pos_id = cursor.lastrowid
        inserted_pos += 1

        for req in job.get("requirements", []):
            cursor.execute(insert_req_sql, (
                pos_id,
                req.get("module", "专业能力"),
                req.get("dimension", "集成电路核心工程"),
                req.get("item_name", f"{title} 核心专业技能要求"),
                req.get("item_type", "must_have"),
                req.get("importance_stars", 5),
                req.get("raw_text", title),
                req.get("structured_analysis", job.get("summary", "")),
                req.get("keywords", ""),
                req.get("sort_order", 1)
            ))
            inserted_req += 1

    conn.commit()
    print(f"Successfully inserted {inserted_pos} positions and {inserted_req} requirements.")

    # 3. 统计全库状态
    cursor.execute("SELECT count(*) FROM job_positions")
    total_pos = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM job_requirements")
    total_req = cursor.fetchone()[0]
    print(f"\n==========================================")
    print(f"DB Total: {total_pos} positions, {total_req} requirements")
    print(f"==========================================")

    # 4. 列出各公司岗位数分布
    cursor.execute("""
        SELECT company_name, count(*) as cnt 
        FROM job_positions 
        GROUP BY company_name 
        ORDER BY cnt ASC
    """)
    print("\n--- Company Job Position Distribution ---")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row[0]}: {row[1]} 岗")

    print(f"\nTotal companies: {len(rows)}")
    min_cnt = min(r[1] for r in rows)
    max_cnt = max(r[1] for r in rows)
    print(f"Minimum jobs per company: {min_cnt}")
    print(f"Maximum jobs per company: {max_cnt}")

    # 5. 校验 source_image 前缀规范
    cursor.execute("SELECT count(*) FROM job_positions WHERE source_image NOT LIKE 'https://www.zhipin.com/web/geek/jobs?city=101210100&query=%'")
    non_std_urls = cursor.fetchone()[0]
    print(f"Non-standard source URLs count: {non_std_urls} (should be 0)")

    conn.close()

if __name__ == "__main__":
    main()

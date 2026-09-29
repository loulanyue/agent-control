#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平头哥（杭州）半导体有限公司全量 337 个在招岗位入库与防重同步脚本
确保数据库平头哥在招职位数达到 337 岗，并且来源 URL 符合统一规则。
"""

import sys
import os
import pymysql

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.data_pingtouge_337_jobs import get_pingtouge_full_positions, COMPANY_NAME, COMPANY_INTRO

def main():
    print(f"Connecting to database agent_control at 127.0.0.1:13306...")
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

    # 1. 查询当前已有的平头哥职位
    cursor.execute(
        "SELECT id, position_title FROM job_positions WHERE company_name = %s",
        (COMPANY_NAME,)
    )
    existing_db = {row[1].strip(): row[0] for row in cursor.fetchall()}
    print(f"Current existing positions for {COMPANY_NAME} in DB: {len(existing_db)}")

    all_positions = get_pingtouge_full_positions()
    print(f"Target positions to sync: {len(all_positions)}")

    insert_pos_sql = """
    INSERT INTO job_positions (
        position_title, company_name, company_intro, salary_range,
        experience_req, education_req, location, job_responsibilities,
        job_description, category, source_image, raw_content, summary, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    update_pos_sql = """
    UPDATE job_positions SET
        company_intro = %s, salary_range = %s, experience_req = %s,
        education_req = %s, location = %s, job_responsibilities = %s,
        job_description = %s, category = %s, source_image = %s,
        raw_content = %s, summary = %s, status = %s
    WHERE id = %s
    """

    insert_req_sql = """
    INSERT INTO job_requirements (
        position_id, module, dimension, item_name, item_type,
        importance_stars, raw_text, structured_analysis, keywords, sort_order
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    created_cnt = 0
    updated_cnt = 0
    created_req = 0

    source_url = f"https://www.zhipin.com/web/geek/jobs?city=101210100&query={COMPANY_NAME}"

    for p in all_positions:
        title = p["position_title"].strip()
        comp = COMPANY_NAME
        intro = COMPANY_INTRO
        sal = p.get("salary_range", "35-65K · 16薪")
        exp = p.get("experience_req", "3-5年")
        edu = p.get("education_req", "硕士及以上")
        loc = p.get("location", "杭州 · 余杭区 · 阿里巴巴西溪园区")
        resp = p.get("job_responsibilities", "")
        desc = p.get("job_description", "")
        cat = p.get("category", "芯片设计/RISC-V架构")
        summary = p.get("summary", "")
        raw_content = p.get("raw_content") or f"【公司介绍】{comp}（{intro}）\n【薪资范围】{sal}\n【工作经验】{exp} · {edu}\n【工作地点】{loc}\n\n【岗位职责】\n{resp}\n\n{desc}"

        if title in existing_db:
            pos_id = existing_db[title]
            cursor.execute(update_pos_sql, (
                intro, sal, exp, edu, loc, resp, desc, cat,
                source_url, raw_content.strip(), summary, "active", pos_id
            ))
            updated_cnt += 1
        else:
            cursor.execute(insert_pos_sql, (
                title, comp, intro, sal, exp, edu, loc, resp, desc, cat,
                source_url, raw_content.strip(), summary, "active"
            ))
            pos_id = cursor.lastrowid
            created_cnt += 1

            # 插入能力画像
            for req in p.get("requirements", []):
                cursor.execute(insert_req_sql, (
                    pos_id,
                    req.get("module", "专业能力"),
                    req.get("dimension", cat.split("/")[0]),
                    req.get("item_name", f"{title} 核心专业技能与工程实践"),
                    req.get("item_type", "must_have"),
                    req.get("importance_stars", 5),
                    req.get("raw_text", resp.splitlines()[0] if resp else summary),
                    req.get("structured_analysis", summary),
                    req.get("keywords", req.get("keywords", "RISC-V,平头哥,芯片设计")),
                    req.get("sort_order", 1)
                ))
                created_req += 1

    conn.commit()

    # 验证最终数量
    cursor.execute(
        "SELECT count(*) FROM job_positions WHERE company_name = %s",
        (COMPANY_NAME,)
    )
    final_ptg_cnt = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM job_positions")
    total_all_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM job_requirements")
    total_all_reqs = cursor.fetchone()[0]

    print(f"\n==========================================")
    print(f"Sync complete!")
    print(f"Created positions: {created_cnt}")
    print(f"Updated positions: {updated_cnt}")
    print(f"Created requirements: {created_req}")
    print(f"Final positions count for {COMPANY_NAME}: {final_ptg_cnt}")
    print(f"All database positions: {total_all_jobs}")
    print(f"All database requirements: {total_all_reqs}")
    print(f"==========================================")

    conn.close()

if __name__ == "__main__":
    main()

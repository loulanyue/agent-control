#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5 家半导体公司精准岗位补充入库与防重同步脚本
1. 杰华特微电子股份有限公司: 112 岗 (总目标 142 岗)
2. 杭州芯云半导体集团有限公司: 36 岗 (总目标 64 岗)
3. 杭州行芯科技有限公司: 18 岗 (总目标 46 岗)
4. 浙江地芯引力科技有限公司: 6 岗 (总目标 31 岗)
5. 杭州国科微电子有限公司: 119 岗 (总目标 144 岗)
合计新增 291 岗，全库达到 1,521 岗！
"""

import sys
import os
import pymysql

# 确保脚本目录在 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_supplement_5_companies import SUPPLEMENT_5_COMPANIES_JOBS

COMPANY_INTROS = {
    "杰华特微电子股份有限公司": "已上市 · 1000-9999人 · 芯片设计/集成电路 · 高性能模拟与数模混合芯片研发上市龙头",
    "杭州芯云半导体集团有限公司": "高新技术企业 · 100-499人 · 芯片封测 · 独立第三方高端集成电路测试与工程服务平台",
    "杭州行芯科技有限公司": "自主创新EDA领军企业 · 100-499人 · 软件开发/EDA · 全流程物理验证与Signoff签名工具领军者",
    "浙江地芯引力科技有限公司": "高新技术企业 · 100-499人 · 芯片设计/射频混合 · 专注于移动通信射频前端芯片与智能快充芯片",
    "杭州国科微电子有限公司": "重点半导体/芯片/集成电路企业 · 固态存储主控、超高清音视频解码与车载智能视觉芯片领军企业",
}

TARGET_COUNTS = {
    "杰华特微电子股份有限公司": 142,
    "杭州芯云半导体集团有限公司": 64,
    "杭州行芯科技有限公司": 46,
    "浙江地芯引力科技有限公司": 31,
    "杭州国科微电子有限公司": 144,
}

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

    # 1. 查询当前已有的职位
    cursor.execute("SELECT id, company_name, position_title FROM job_positions")
    existing_db = {}
    for pos_id, comp, title in cursor.fetchall():
        existing_db[(comp.strip(), title.strip())] = pos_id

    print(f"Total existing positions in DB before sync: {len(existing_db)}")

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

    for p in SUPPLEMENT_5_COMPANIES_JOBS:
        comp = p["company_name"].strip()
        title = p["position_title"].strip()
        intro = COMPANY_INTROS.get(comp, "知名半导体企业")
        sal = p.get("salary_range", "30-55K · 16薪")
        exp = p.get("experience_req", "3-5年")
        edu = p.get("education_req", "本科及以上")
        loc = p.get("location", "杭州")
        resp = p.get("job_responsibilities", "")
        desc = p.get("job_description", "")
        cat = p.get("category", "芯片设计")
        summary = p.get("summary", "")
        source_url = f"https://www.zhipin.com/web/geek/jobs?city=101210100&query={comp}"
        raw_content = p.get("raw_content") or f"【公司介绍】{comp}（{intro}）\n【薪资范围】{sal}\n【工作经验】{exp} · {edu}\n【工作地点】{loc}\n\n【岗位职责】\n{resp}\n\n{desc}"

        key = (comp, title)
        if key in existing_db:
            pos_id = existing_db[key]
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
            existing_db[key] = pos_id

            # 插入能力画像
            for req in p.get("requirements", []):
                cursor.execute(insert_req_sql, (
                    pos_id,
                    req.get("module", "专业能力"),
                    req.get("dimension", cat.split("/")[0]),
                    req.get("item_name", f"{title} 核心专业技能与工程实践"),
                    req.get("item_type", req.get("item_type", "must_have")),
                    req.get("importance_stars", req.get("importance_stars", 5)),
                    req.get("raw_text", req.get("raw_text", summary)),
                    req.get("structured_analysis", req.get("structured_analysis", summary)),
                    req.get("keywords", req.get("keywords", "集成电路,半导体")),
                    req.get("sort_order", req.get("sort_order", 1))
                ))
                created_req += 1

    conn.commit()

    print("\n==========================================")
    print("Sync complete!")
    print(f"Created positions: {created_cnt}")
    print(f"Updated positions: {updated_cnt}")
    print(f"Created requirements: {created_req}")

    print("\nVerifying each target company:")
    all_ok = True
    for comp, target in TARGET_COUNTS.items():
        cursor.execute("SELECT count(*) FROM job_positions WHERE company_name = %s", (comp,))
        actual = cursor.fetchone()[0]
        status = "✅ MATCH" if actual == target else f"❌ MISMATCH (expected {target})"
        if actual != target:
            all_ok = False
        print(f" - {comp}: {actual} / {target} -> {status}")

    cursor.execute("SELECT count(*) FROM job_positions")
    total_jobs = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM job_requirements")
    total_reqs = cursor.fetchone()[0]

    print(f"\nTotal positions in DB: {total_jobs} (Expected: 1521)")
    print(f"Total requirements in DB: {total_reqs}")
    print(f"All targets met: {'YES ✅' if all_ok and total_jobs == 1521 else 'NO ❌'}")
    print("==========================================")

    conn.close()

if __name__ == "__main__":
    main()

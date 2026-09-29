#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 5 家公司的指定岗位补充数据:
1. 杰华特微电子股份有限公司 (当前 30 -> 目标 142, 需新增 112)
2. 杭州芯云半导体集团有限公司 (当前 28 -> 目标 64, 需新增 36)
3. 杭州行芯科技有限公司 (当前 28 -> 目标 46, 需新增 18)
4. 浙江地芯引力科技有限公司 (当前 25 -> 目标 31, 需新增 6)
5. 杭州国科微电子有限公司 (当前 25 -> 目标 144, 需新增 119)
合计新增 291 岗，全库达到 1,521 岗！
"""

import sys
import os
import pymysql

# 查询现有职位标题以保证完全去重
conn = pymysql.connect(host='127.0.0.1', port=13306, user='root', password='', db='agent_control')
cursor = conn.cursor()
cursor.execute("SELECT company_name, position_title FROM job_positions")
existing_map = {}
for c, t in cursor.fetchall():
    existing_map.setdefault(c, set()).add(t.strip())
conn.close()

# 辅助生成器
def make_item(comp, title, cat, sal, exp, edu, loc, summary, kw, resp):
    return {
        "company_name": comp,
        "position_title": title,
        "category": cat,
        "salary_range": sal,
        "experience_req": exp,
        "education_req": edu,
        "location": loc,
        "job_responsibilities": resp,
        "job_description": f"【任职资格】\n1、{edu}学历，具备{exp}相关行业经验；\n2、熟练掌握{kw}等核心技能，具有良好的团队沟通与工程攻关能力。\n工作地点：{loc}。",
        "source_image": f"https://www.zhipin.com/web/geek/jobs?city=101210100&query={comp}",
        "summary": summary,
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": cat.split("/")[0],
                "item_name": f"{title} 核心专业技能与工程实践",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": resp.splitlines()[0] if resp else summary,
                "structured_analysis": summary,
                "keywords": kw,
                "sort_order": 1
            }
        ]
    }

print("Loaded existing titles from DB. Ready to define specs.")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def make_job(comp, title, cat, sal, exp, edu, loc, summary, kw, resp):
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
                "item_name": f"{title} 核心专业能力与工程实践",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": resp.splitlines()[0] if resp else summary,
                "structured_analysis": summary,
                "keywords": kw,
                "sort_order": 1
            }
        ]
    }

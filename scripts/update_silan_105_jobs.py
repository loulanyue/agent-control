#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行杭州士兰微电子股份有限公司 105 个全量在招岗位及能力画像落库与严格幂等更新
"""

import sys
import os
import logging

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from db.session import SessionLocal
from app.models.extensions import JobPosition, JobRequirement
from sqlalchemy import func, text
from scripts.data_silan_105_jobs import SILAN_105_POSITIONS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

COMPANY_NAME = "杭州士兰微电子股份有限公司"
COMPANY_INTRO = "已上市(600460) · 5000-9999人 · 半导体IDM龙头企业 · 专注于硅半导体、功率器件、集成电路及化合物半导体研发与制造"
LOCATION_DEFAULT = "杭州 · 钱塘区 · 士兰微产业园 / 滨江区"

def import_silan_105_jobs():
    db = SessionLocal()
    created_count = 0
    updated_count = 0
    created_reqs = 0
    updated_reqs = 0

    try:
        logger.info(f"开始同步与补全 [{COMPANY_NAME}] 全量 {len(SILAN_105_POSITIONS)} 个在招岗位...")

        for p_data in SILAN_105_POSITIONS:
            title = p_data["position_title"].strip()
            category = p_data["category"].strip()

            pos = db.query(JobPosition).filter(
                JobPosition.company_name == COMPANY_NAME,
                JobPosition.position_title == title
            ).first()

            raw_content = p_data.get("raw_content")
            if not raw_content:
                raw_content = f"【公司介绍】{COMPANY_NAME}（{COMPANY_INTRO}）\n【薪资范围】{p_data.get('salary_range', '')}\n【工作经验】{p_data.get('experience_req', '')} · {p_data.get('education_req', '')}\n【工作地点】{p_data.get('location', '')}\n\n【岗位职责】\n{p_data.get('job_responsibilities', '')}\n\n{p_data.get('job_description', '')}"

            if not pos:
                pos = JobPosition(
                    position_title=title,
                    company_name=COMPANY_NAME,
                    company_intro=COMPANY_INTRO,
                    salary_range=p_data.get("salary_range", ""),
                    experience_req=p_data.get("experience_req", ""),
                    education_req=p_data.get("education_req", ""),
                    location=p_data.get("location", LOCATION_DEFAULT),
                    job_responsibilities=p_data.get("job_responsibilities", ""),
                    job_description=p_data.get("job_description", ""),
                    category=category,
                    source_image=p_data.get("source_image", ""),
                    raw_content=raw_content.strip(),
                    summary=p_data.get("summary", ""),
                    status=p_data.get("status", "active")
                )
                db.add(pos)
                db.flush()
                created_count += 1
                logger.info(f"新建士兰微岗位: [{pos.id}] {title}")
            else:
                pos.company_name = COMPANY_NAME
                pos.company_intro = COMPANY_INTRO
                pos.salary_range = p_data.get("salary_range", pos.salary_range)
                pos.experience_req = p_data.get("experience_req", pos.experience_req)
                pos.education_req = p_data.get("education_req", pos.education_req)
                pos.location = p_data.get("location", pos.location)
                pos.job_responsibilities = p_data.get("job_responsibilities", pos.job_responsibilities)
                pos.job_description = p_data.get("job_description", pos.job_description)
                pos.category = category
                pos.source_image = p_data.get("source_image", pos.source_image)
                pos.raw_content = raw_content.strip()
                pos.summary = p_data.get("summary", pos.summary)
                pos.status = p_data.get("status", "active")
                db.flush()
                updated_count += 1
                logger.info(f"更新士兰微岗位: [{pos.id}] {title}")

            # 处理能力要素画像
            requirements = p_data.get("requirements", [])
            for req_data in requirements:
                item_name = req_data["item_name"].strip()
                req = db.query(JobRequirement).filter(
                    JobRequirement.position_id == pos.id,
                    JobRequirement.item_name == item_name
                ).first()

                if not req:
                    req = JobRequirement(
                        position_id=pos.id,
                        module=req_data.get("module", "专业能力").strip(),
                        dimension=req_data.get("dimension", "核心专业能力").strip(),
                        item_name=item_name,
                        item_type=req_data.get("item_type", "must_have"),
                        importance_stars=req_data.get("importance_stars", 5),
                        raw_text=req_data.get("raw_text", "").strip(),
                        structured_analysis=req_data.get("structured_analysis", ""),
                        keywords=req_data.get("keywords", ""),
                        sort_order=req_data.get("sort_order", 1)
                    )
                    db.add(req)
                    created_reqs += 1
                else:
                    req.module = req_data.get("module", req.module).strip()
                    req.dimension = req_data.get("dimension", req.dimension).strip()
                    req.item_type = req_data.get("item_type", req.item_type)
                    req.importance_stars = req_data.get("importance_stars", req.importance_stars)
                    req.raw_text = req_data.get("raw_text", req.raw_text).strip()
                    req.structured_analysis = req_data.get("structured_analysis", req.structured_analysis)
                    req.keywords = req_data.get("keywords", req.keywords)
                    updated_reqs += 1

        db.commit()

        # 验证最终数据库状态
        final_count = db.query(func.count(JobPosition.id)).filter(
            JobPosition.company_name == COMPANY_NAME
        ).scalar()
        all_count = db.query(func.count(JobPosition.id)).scalar()

        logger.info(f"同步完成！新建岗位 {created_count} 个，更新岗位 {updated_count} 个。")
        logger.info(f"当前 [{COMPANY_NAME}] 数据库岗位总数: {final_count} 个 (全库总计: {all_count} 个)")

        assert final_count == 105, f"Expected exactly 105 positions for Silan, but got {final_count}"
        return {
            "success": True,
            "created_count": created_count,
            "updated_count": updated_count,
            "final_count": final_count,
            "all_count": all_count
        }
    except Exception as e:
        db.rollback()
        logger.exception(f"更新士兰微105个岗位失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import_silan_105_jobs()

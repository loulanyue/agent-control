#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
杭州人才公示数据按 (申报人, 出生年月, 工作单位) 去重脚本
保留每组中最近更新的数据 (updated_at DESC, publish_date DESC, id DESC)
"""

import os
import sys
import argparse
import logging

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from db.session import SessionLocal
from app.models.extensions import HzTalentNotice
from sqlalchemy import func

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("deduplicate-talent")

def deduplicate(dry_run: bool = False):
    db = SessionLocal()
    try:
        total_before = db.query(func.count(HzTalentNotice.id)).scalar()
        logger.info(f"去重前总记录数: {total_before}")

        # 查找存在重复的 (person_name, birth_date, work_unit) 分组 (排除清单类占位数据)
        dup_groups = db.query(
            HzTalentNotice.person_name,
            HzTalentNotice.birth_date,
            HzTalentNotice.work_unit,
            func.count(HzTalentNotice.id).label("cnt")
        ).filter(
            HzTalentNotice.person_name.isnot(None),
            HzTalentNotice.person_name != "",
            HzTalentNotice.person_name != "详见清单"
        ).group_by(
            HzTalentNotice.person_name,
            HzTalentNotice.birth_date,
            HzTalentNotice.work_unit
        ).having(func.count(HzTalentNotice.id) > 1).all()

        logger.info(f"发现重复分组数: {len(dup_groups)}")

        delete_ids = []
        keep_ids = []

        for group in dup_groups:
            pname, bdate, unit = group[0], group[1], group[2]
            # 按更新时间、发布日期、自增ID降序排序，排在第一位的为最近更新的数据
            records = db.query(HzTalentNotice).filter(
                HzTalentNotice.person_name == pname,
                HzTalentNotice.birth_date == bdate,
                HzTalentNotice.work_unit == unit
            ).order_by(
                HzTalentNotice.updated_at.desc(),
                HzTalentNotice.publish_date.desc(),
                HzTalentNotice.id.desc()
            ).all()

            kept = records[0]
            keep_ids.append(kept.id)
            for dup in records[1:]:
                delete_ids.append(dup.id)

        logger.info(f"待保留记录数: {len(keep_ids)}, 待删除重复记录数: {len(delete_ids)}")

        if not dry_run and delete_ids:
            # 批量删除多余的旧记录
            batch_size = 500
            for i in range(0, len(delete_ids), batch_size):
                chunk = delete_ids[i:i + batch_size]
                db.query(HzTalentNotice).filter(HzTalentNotice.id.in_(chunk)).delete(synchronize_session=False)
            db.commit()
            total_after = db.query(func.count(HzTalentNotice.id)).scalar()
            logger.info(f"去重成功! 实际删除记录: {len(delete_ids)}, 去重后总记录数: {total_after}")
        elif dry_run:
            logger.info(f"[Dry Run] 未实际删除数据，若执行将删除 {len(delete_ids)} 条记录")
        else:
            logger.info("未发现需要删除的重复数据")

    except Exception as e:
        db.rollback()
        logger.error(f"去重执行失败: {e}", exc_info=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="杭州人才申报公示去重脚本")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际删除数据")
    args = parser.parse_args()
    deduplicate(dry_run=args.dry_run)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 job_positions 和 job_requirements 添加唯一性约束，确保数据绝不重复
"""

import sys
import os
import logging
from sqlalchemy import text

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from db.session import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def apply_constraints():
    db = SessionLocal()
    try:
        logger.info("检查并清理 job_positions 中的潜在重复数据...")
        # 1. 查找重复数据
        dups = db.execute(text("""
            SELECT company_name, position_title, COUNT(*) as cnt
            FROM job_positions
            GROUP BY company_name, position_title
            HAVING cnt > 1
        """)).fetchall()

        if dups:
            logger.warning(f"发现 {len(dups)} 组重复岗位，执行保留最新记录并清理其余重复项...")
            for comp, title, cnt in dups:
                records = db.execute(text("""
                    SELECT id FROM job_positions 
                    WHERE company_name = :comp AND position_title = :title
                    ORDER BY id DESC
                """), {"comp": comp, "title": title}).fetchall()
                keep_id = records[0][0]
                remove_ids = [r[0] for r in records[1:]]
                logger.info(f"公司 [{comp}] 岗位 [{title}]: 保留 ID={keep_id}, 删除重复 IDs={remove_ids}")
                # 删除关联 requirements
                db.execute(text("""
                    DELETE FROM job_requirements WHERE position_id IN :remove_ids
                """), {"remove_ids": tuple(remove_ids)})
                # 删除重复 position
                db.execute(text("""
                    DELETE FROM job_positions WHERE id IN :remove_ids
                """), {"remove_ids": tuple(remove_ids)})
            db.commit()
            logger.info("重复岗位清理完成！")
        else:
            logger.info("job_positions 无重复数据，干净整洁。")

        # 2. 检查并清理 job_requirements 中的潜在重复项
        req_dups = db.execute(text("""
            SELECT position_id, item_name, COUNT(*) as cnt
            FROM job_requirements
            GROUP BY position_id, item_name
            HAVING cnt > 1
        """)).fetchall()

        if req_dups:
            logger.warning(f"发现 {len(req_dups)} 组重复能力要素，执行清理...")
            for pid, iname, cnt in req_dups:
                r_records = db.execute(text("""
                    SELECT id FROM job_requirements
                    WHERE position_id = :pid AND item_name = :iname
                    ORDER BY id DESC
                """), {"pid": pid, "iname": iname}).fetchall()
                r_keep = r_records[0][0]
                r_remove = [r[0] for r in r_records[1:]]
                db.execute(text("""
                    DELETE FROM job_requirements WHERE id IN :r_remove
                """), {"r_remove": tuple(r_remove)})
            db.commit()
            logger.info("重复能力要素清理完成！")
        else:
            logger.info("job_requirements 无重复数据，干净整洁。")

        # 3. 检查并为 job_positions 添加唯一约束
        indexes_pos = [r[2] for r in db.execute(text("SHOW INDEX FROM job_positions")).fetchall()]
        if "uniq_company_position" not in indexes_pos:
            logger.info("正在为 job_positions 添加唯一索引: uniq_company_position(company_name, position_title)...")
            db.execute(text("""
                ALTER TABLE job_positions 
                ADD UNIQUE KEY uniq_company_position (company_name, position_title)
            """))
            db.commit()
            logger.info("成功创建唯一索引 uniq_company_position！")
        else:
            logger.info("唯一索引 uniq_company_position 已存在。")

        # 4. 检查并为 job_requirements 添加唯一约束
        indexes_req = [r[2] for r in db.execute(text("SHOW INDEX FROM job_requirements")).fetchall()]
        if "uniq_pos_item" not in indexes_req:
            logger.info("正在为 job_requirements 添加唯一索引: uniq_pos_item(position_id, item_name(191))...")
            db.execute(text("""
                ALTER TABLE job_requirements 
                ADD UNIQUE KEY uniq_pos_item (position_id, item_name(191))
            """))
            db.commit()
            logger.info("成功创建唯一索引 uniq_pos_item！")
        else:
            logger.info("唯一索引 uniq_pos_item 已存在。")

        logger.info("唯一性约束部署完成，数据库已具备原生防重防御能力！")
    except Exception as e:
        db.rollback()
        logger.exception(f"配置唯一性约束失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    apply_constraints()

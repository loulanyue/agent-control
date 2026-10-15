import sys
import os
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.session import SessionLocal
from app.models.extensions import HzTalentNotice
from scripts.deduplicate_talent_notices import deduplicate

def test_deduplicate_talent_notices():
    db = SessionLocal()
    test_notice_1 = "test_dup_001"
    test_notice_2 = "test_dup_002"
    
    # 清理可能残留的测试数据
    db.query(HzTalentNotice).filter(HzTalentNotice.notice_id.in_([test_notice_1, test_notice_2])).delete(synchronize_session=False)
    db.commit()

    now = datetime.utcnow()
    # 插入两条相同的 (申报人, 出生年月, 工作单位) 数据
    r1 = HzTalentNotice(
        notice_id=test_notice_1,
        notice_type="personal",
        title="关于测试张三申报公示(旧)",
        person_name="测试去重张三",
        birth_date="1992年05月",
        work_unit="杭州测试人工智能科技有限公司",
        publish_date=date(2026, 8, 1),
        detail_url="https://example.com/1",
        crawl_batch="test_batch_1",
        last_crawl_batch="test_batch_1",
        created_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=2)
    )
    r2 = HzTalentNotice(
        notice_id=test_notice_2,
        notice_type="personal",
        title="关于测试张三申报公示(新)",
        person_name="测试去重张三",
        birth_date="1992年05月",
        work_unit="杭州测试人工智能科技有限公司",
        publish_date=date(2026, 9, 1),
        detail_url="https://example.com/2",
        crawl_batch="test_batch_2",
        last_crawl_batch="test_batch_2",
        created_at=now,
        updated_at=now
    )
    db.add_all([r1, r2])
    db.commit()

    # 执行去重
    deduplicate(dry_run=False)

    # 验证: 应仅保留最新一条 (r2)，旧数据 (r1) 被删除
    remaining = db.query(HzTalentNotice).filter(
        HzTalentNotice.person_name == "测试去重张三",
        HzTalentNotice.birth_date == "1992年05月",
        HzTalentNotice.work_unit == "杭州测试人工智能科技有限公司"
    ).all()

    assert len(remaining) == 1, f"Expected 1 record after deduplication, got {len(remaining)}"
    assert remaining[0].notice_id == test_notice_2, f"Expected to keep {test_notice_2}, but got {remaining[0].notice_id}"
    assert remaining[0].title == "关于测试张三申报公示(新)"

    # 清理测试数据
    db.query(HzTalentNotice).filter(HzTalentNotice.notice_id == test_notice_2).delete(synchronize_session=False)
    db.commit()
    db.close()

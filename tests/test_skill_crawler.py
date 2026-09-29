import sys
import os
sys.path.insert(0, "/Users/youfanyu/Desktop/workspace/tpm/agent_control")

# 引入爬虫服务
sys.path.insert(0, "/Users/youfanyu/Desktop/workspace/tpm/.agents/skills/hz-talent-crawler/scripts")
from crawler import HzTalentCrawlerService

def test_parser():
    service = HzTalentCrawlerService()
    text = "陈强（工作单位：浙江大华技术股份有限公司；受理部门：滨江区人力社保局），男，1988年05月出生，申报D类（具有博士学位）高层次人才，现予公示，公示期为：2026年9月7日至2026年9月11日。"
    title = "关于陈强申报高层次人才的公示"
    notice_id = "test_parse_001"
    res = service.parse_personal_notice(notice_id, title, text, "<p>demo</p>")
    
    assert res["person_name"] == "陈强"
    assert res["gender"] == "男"
    assert res["birth_date"] == "1988年05月"
    assert res["work_unit"] == "浙江大华技术股份有限公司"
    assert res["accept_dept"] == "滨江区人力社保局"
    assert "D类" in res["apply_type"]
    assert "2026年9月7日" in res["publicity_period"]
    print("Parser test passed successfully!")

def test_foreign_name_parser():
    service = HzTalentCrawlerService()
    # 真实案例：https://rchkt.hrss.hangzhou.gov.cn/#/hzrc/detail?no=2609280749589
    text = "GRYNYUK ANDRII （工作单位： 浙江巴顿焊接技术研究院 ；受理部门：萧山区审管办），男，1972年10月出生，申报 D 类（ 杭州市政府“钱江友谊奖”获得者 ）高层次人才，现予公示，公示期三天。公示期间，任何单位和个人均可通过来信、来电、来访等多种形式向市人力社保局反映对象存在的问题。 地址：杭州市解放东路18号市民中心D座1903室 邮编： 310026 电话： 85253557 杭州市人力资源和社会保障局 2026年09月28日"
    title = "关于GRYNYUK ANDRII申报高层次人才的公示"
    notice_id = "2609280749589"
    res = service.parse_personal_notice(notice_id, title, text, "<p>demo</p>")

    assert res["person_name"] == "GRYNYUK ANDRII"
    assert res["gender"] == "男"
    assert res["birth_date"] == "1972年10月"
    assert res["work_unit"] == "浙江巴顿焊接技术研究院"
    assert res["accept_dept"] == "萧山区审管办"
    assert res["apply_type"] == "D类（杭州市政府“钱江友谊奖”获得者）"
    print("Foreign name parser test passed successfully!")

if __name__ == "__main__":
    test_parser()
    test_foreign_name_parser()


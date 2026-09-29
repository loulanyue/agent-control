# -*- coding: utf-8 -*-
"""
浙江地芯引力科技有限公司 补充岗位数据 (6 岗)
当前库内 25 岗 -> 目标 31 岗
"""

COMPANY = "浙江地芯引力科技有限公司"
LOCATION = "杭州 · 滨江区 · 长河"

specs = [
    ("高精度低噪声Delta-Sigma ADC模拟设计专家", "模拟芯片设计/ADC", "35-65K · 15薪", "5-10年", "硕士及以上",
     "负责高精度、低功耗Delta-Sigma模数转换器(ADC)微架构设计与晶圆流片验证。", "Delta-Sigma,ADC,低噪声,运放,采样保持,MATLAB",
     "1、负责高阶单比特/多比特Delta-Sigma调制器架构设计与噪声整形仿真；\n2、主导斩波稳零放大器(Chopper OpAmp)与低温漂基准源电路实现；\n3、协同数字后端完成抽取滤波器(Decimation Filter)数模协同验证。"),

    ("USB-PD3.1协议控制器数字验证工程师", "数字IC设计/验证", "25-45K · 15薪", "3-5年", "本科及以上",
     "负责USB PD3.1/UFCS融合快充协议控制器数字前端逻辑的UVM自动化验证平台搭建。", "UVM,SystemVerilog,USB-PD,数字验证,覆盖率",
     "1、基于SystemVerilog搭建UVM受约束随机测试平台与协议断言(SVA)库；\n2、制定详细验证计划，达成100%功能覆盖率与代码覆盖率闭环；\n3、构建数模混合仿真(AMS)测试用例，验证数字控制器与高压模拟接口交互。"),

    ("大功率双向同步升降压(Buck-Boost)控制算法工程师", "电源管理/控制算法", "30-55K · 15薪", "3-5年", "硕士及以上",
     "负责百瓦级双向大功率Buck-Boost快充转换器控制环路设计与动态响应优化。", "Buck-Boost,双向电源,控制环路,快充,补偿网络,SIMPLIS",
     "1、负责4开关Buck-Boost平滑模式切换逻辑与宽输入输出动态环路补偿；\n2、解决高频轻载PFM与重载PWM高效平稳切换与纹波抑制问题；\n3、运用SIMPLIS/Saber建立精确小信号模型，指导模拟核心设计。"),

    ("汽车级低压差线性稳压器(LDO)版图设计资深工程师", "模拟IC版图/Layout", "20-35K · 15薪", "5-8年", "本科及以上",
     "负责车规级超低噪声、高PSRR大电流LDO模拟芯片版图物理实现与DRC/LVS/ERC闭环。", "版图设计,LDO,高PSRR,BCD工艺,电迁移,Virtuoso",
     "1、负责BCD工艺下大功率调整管阵列对称布局与极低寄生阻抗走线；\n2、严格进行静电防护(ESD)与闩锁效应(Latch-up)加固版图规划；\n3、攻克高频PSRR敏感节点屏蔽与大电流寄生压降(IR-Drop)收敛。"),

    ("智能手机快充电源芯片测试开发高级工程师", "芯片测试/ATE开发", "22-40K · 15薪", "3-5年", "本科及以上",
     "负责快充协议芯片及低阻抗MOS驱动芯片ATE量产测试方案开发与良率提升。", "ATE测试,Chroma,STS8200,量产测试,测试板设计,良率",
     "1、主导STS8200/Chroma测试机台多工位并测(Multi-site)程序编写与调试；\n2、设计低插损测试接口板(Loadboard)与大电流老化板(BIB)；\n3、分析量产WAT及CP测试数据，协同晶圆代工厂排查失效机制。"),

    ("电池充放电管理芯片现场应用支持专家", "系统应用/FAE", "25-45K · 15薪", "5-8年", "本科及以上",
     "负责储能电源、智能穿戴及消费数码客户方案导入与现场技术攻坚。", "FAE,应用支持,电池管理,快充方案,方案落地,客户支持",
     "1、支持终端客户完成快充电路原理图、PCB布局设计与关键器件选型；\n2、排查客户现场快充握手失败、温升异常及电磁干扰(EMI)超标问题；\n3、汇总市场技术痛点，输出极具竞争力的竞品分析报告与Demo方案。"),
]

def get_dixin_jobs():
    items = []
    for title, cat, sal, exp, edu, summary, kw, resp in specs:
        items.append({
            "company_name": COMPANY,
            "position_title": title,
            "category": cat,
            "salary_range": sal,
            "experience_req": exp,
            "education_req": edu,
            "location": LOCATION,
            "job_responsibilities": resp,
            "job_description": f"【岗位职责】\n{resp}\n\n【任职资格】\n1、{edu}学历，具备{exp}相关行业经验；\n2、熟练掌握{kw}等核心技能，具有良好的团队沟通与工程攻关能力。\n工作地点：{LOCATION}。",
            "source_image": f"https://www.zhipin.com/web/geek/jobs?city=101210100&query={COMPANY}",
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
                },
                {
                    "module": "工程经验",
                    "dimension": "研发经验",
                    "item_name": f"{exp}芯片设计与工程量产落地经验",
                    "item_type": "must_have",
                    "importance_stars": 4,
                    "raw_text": f"具备{exp}集成电路领域实战经验，参与或主导过完整芯片量产周期。",
                    "structured_analysis": f"要求具备{exp}实操经验与扎实的数模混合芯片研发背景。",
                    "keywords": kw.split(",")[0] if kw else "芯片研发",
                    "sort_order": 2
                }
            ]
        })
    return items

if __name__ == "__main__":
    jobs = get_dixin_jobs()
    print(f"Loaded {len(jobs)} jobs for {COMPANY}")

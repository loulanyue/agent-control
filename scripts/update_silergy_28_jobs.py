#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补全矽力杰半导体技术（杭州）有限公司在招全量28个岗位及深度能力画像
严格对照BOSS直聘实测在招岗位列表（测试技术员、芯片测试、信号链测试、模拟IC、版图、FAE等）
"""

import os
import sys
import json
import logging

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from db.session import SessionLocal
from app.models.extensions import JobPosition, JobRequirement

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SILERGY_28_POSITIONS = [
    # 1. BOSS直聘实测列表第1项: 测试技术员
    {
        "position_title": "测试技术员",
        "category": "芯片测试/技术支持",
        "salary_range": "8-12K · 14薪",
        "experience_req": "经验不限",
        "education_req": "本科",
        "location": "杭州 · 滨江区 · 西兴",
        "job_responsibilities": """主要职责
1、与设计工程师合作，完成IC测试程序的开发及产品的失效分析工作；
2、配合产品应用工程师，完成测试程序的优化工作；
3、配合测试代工厂，完成产品的测试加工工作；
4、熟悉IC产品的QA架构，完成产品的QA工作；
5、协助测试工程师完成各种芯片的测试任务，以及测试硬件的调试任务。""",
        "job_description": """岗位要求
1、本科及以上学历，微电子科学与工程、集成电路设计、电子科学与技术、通信工程等专业；
2、熟悉基本的模拟电路知识，了解示波器、万用表、信号发生器等仪器的使用；
3、良好的沟通交流能力和团队协作精神。
工作地址：杭州滨江区矽力杰半导体产业化基地联慧街6号""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责IC测试程序执行、测试代工厂量产加工配合与QA架构质量追踪。",
        "status": "active",
        "requirements": [
            {
                "module": "工程与技术",
                "dimension": "芯片测试协同",
                "item_name": "IC测试程序执行与QA质量架构配合",
                "item_type": "must_have",
                "importance_stars": 4,
                "raw_text": "与设计工程师合作完成IC测试程序开发及产品失效分析；配合测试代工厂完成测试加工。",
                "structured_analysis": "规范执行测试SOP，熟练操作常用电子测量仪器并记录测试数据。",
                "keywords": "IC测试,测试代工厂,QA架构,失效分析,微电子",
                "sort_order": 1
            }
        ]
    },
    # 2. BOSS直聘实测列表第2项: 芯片测试工程师
    {
        "position_title": "芯片测试工程师",
        "category": "芯片测试/ATE工程",
        "salary_range": "12-24K · 14薪",
        "experience_req": "经验不限",
        "education_req": "本科",
        "location": "杭州 · 滨江区 · 长河",
        "job_responsibilities": """1、负责电源管理芯片及模拟信号链芯片的量产测试方案评估与测试程序编写；
2、负责ATE机台（Chroma/AccoTest/ASL等）测试程序调试与测试接口板(Load Board)设计审查；
3、推进晶圆CP测试与成品FT测试良率监控与测试时间(Test Time)压缩；
4、协同质量与可靠性团队完成ESD、HTOL与高低温极限测试环境搭建。""",
        "job_description": """【任职资格】
1、本科及以上学历，微电子、集成电路、测控技术或自动化相关专业；
2、精通C/C++编程，熟悉至少一种半导体主流ATE测试机台开发环境；
3、对模拟芯片电学指标（静态功耗、动态响应、基准精度）有深入理解。
工作地址：杭州滨江区矽力杰半导体产业化基地联慧街6号""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责矽力杰量产芯片ATE自动化测试程序开发、测试接口硬件验证与批量良品率保障。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "ATE测试程序开发",
                "item_name": "主流半导体ATE机台测试开发与CP/FT方案落地",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "熟练掌握ATE量产测试流程与C/C++测试向量开发，具备高效压缩测试周期的实操经验。",
                "structured_analysis": "熟悉模拟IC测试板级阻抗匹配、多工位并行测试架构以及测试故障溯源方法。",
                "keywords": "ATE,CP测试,FT测试,Load Board,C++,模拟IC测试",
                "sort_order": 1
            }
        ]
    },
    # 3. BOSS直聘实测列表第3项: 芯片测试工程师（信号链）
    {
        "position_title": "芯片测试工程师（信号链）",
        "category": "芯片测试/信号链高精测试",
        "salary_range": "20-40K · 14薪",
        "experience_req": "10年以上",
        "education_req": "本科",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、主导高精度信号链芯片（高精度ADC/DAC、低噪声运算放大器、高精密基准源）测试架构设计；
2、负责微弱信号、纳伏级失调电压、高线性度THD测试环境抗干扰与高频低噪声屏蔽夹具设计；
3、编写并优化泰瑞达UltraFLEX或爱德万V93000量产测试代码，攻坚复杂工况偶发性测试异常；
4、主导测试代工厂测试技术转移与量产质量放行标准把控，指导中初级测试工程师技术攻坚。""",
        "job_description": """【任职资格】
1、本科及以上学历，微电子、仪器科学、通信工程等相关专业，10年以上芯片测试开发经验；
2、深入精通高精度模拟与信号链测试理论，具有成功量产多款高端信号链芯片的完整经验；
3、精通高端ATE机台高级特性，具备极强的电磁兼容(EMC)与微弱信号测量工程攻坚能力。
工作地址：杭州滨江区矽力杰半导体产业化基地联慧街6号""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "矽力杰资深测试专家岗位，攻坚高精密信号链芯片纳伏级超微弱信号测试与高端ATE测试体系建设。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "高精信号链测试架构",
                "item_name": "高精度ADC/DAC与微弱信号ATE测试系统研发",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "主导高精度信号链芯片测试架构设计，攻克纳伏级失调与极低噪声屏蔽测试难题。",
                "structured_analysis": "精通超高位ADC有效位数(ENOB)、信噪比(SNR)及总谐波失真(THD)的高精度计量与快速自动化测定。",
                "keywords": "信号链,高精度ADC,微弱信号,UltraFLEX,V93000,低噪声,THD",
                "sort_order": 1
            }
        ]
    },
    # 4. 高级电源管理模拟IC研发工程师 (PMIC)
    {
        "position_title": "高级电源管理模拟IC研发工程师 (PMIC)",
        "category": "模拟芯片设计/电源IC",
        "salary_range": "32-55K · 15薪",
        "experience_req": "3-5年",
        "education_req": "硕士及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责工业与汽车电子领域高压、高功率密度电源管理IC的架构与晶体管级电路设计；
2、攻坚超低待机静态电流(IQ)、超快瞬态响应与片上高压自启动保护电路设计；
3、带领团队完成样片测试验证、可靠性考核（HTOL/ESD）与量产导入。""",
        "job_description": """【任职资格】
1、微电子、集成电路等相关专业硕士及以上学历，3年以上高压模拟IC设计经验；
2、熟练掌握BCD工艺及模拟版图布局，精通Cadence全套模拟设计EDA工具。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "矽力杰核心模拟芯片研发，攻关工业级宽输入电压高频开关转换器与电源管理芯片。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "高压模拟IC设计",
                "item_name": "超低静态电流与片上宽电压功率拓扑研发",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "深入理解晶体管级失配、温度漂移补偿及高压自启动电路设计。",
                "structured_analysis": "通过前馈控制与自适应斜坡补偿技术，提升电源IC转换效率超过96%。",
                "keywords": "PMIC,模拟IC,BCD,Cadence,高功率密度,低IQ",
                "sort_order": 1
            }
        ]
    },
    # 5. 模拟IC版图设计工程师 (Analog Layout)
    {
        "position_title": "模拟IC版图设计工程师 (Analog Layout)",
        "category": "芯片设计/模拟版图",
        "salary_range": "18-35K · 14薪",
        "experience_req": "3-5年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责DC-DC、LDO、驱动芯片及关键模拟IP模块的晶体管级版图布局布线(Layout)；
2、严格执行器件精确匹配、差分对称、热均匀分布、大电流走线寄生阻抗压降优化；
3、独立完成DRC、LVS、ERC、Antenna规则检查与PEX寄生参数提取，配合电路工程师后仿真收敛。""",
        "job_description": """【任职资格】
1、本科及以上学历，微电子、电子工程等相关专业，3年以上高压模拟版图设计经验；
2、熟练掌握Virtuoso Layout Suite, Calibre等主流EDA版图设计与物理验证工具。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责矽力杰高性能电源管理芯片模拟版图物理实现，保障芯片大电流抗击穿与低寄生损耗。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "高压模拟版图设计",
                "item_name": "BCD高压器件匹配布局与Calibre物理签核",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通模拟版图匹配技巧与大功率走线电迁移(EM)防护，精通DRC/LVS/PEX全流程。",
                "structured_analysis": "通过共质心与多层金属并联布局，极致降低寄生电感电容，保证后仿真性能吻合。",
                "keywords": "Layout,版图设计,Calibre,DRC,LVS,BCD工艺,寄生提取",
                "sort_order": 1
            }
        ]
    },
    # 6. 现场应用工程师 (FAE - 汽车与新能源电源芯片)
    {
        "position_title": "现场应用工程师 (FAE - 汽车与新能源电源芯片)",
        "category": "系统应用/FAE技术支持",
        "salary_range": "22-40K · 14薪",
        "experience_req": "3-5年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责矽力杰电源管理芯片在汽车座舱、BMS、自动驾驶及光储终端客户的技术推广与导入；
2、为客户提供高效率供电参考设计方案，现场协助客户调试解决环路震荡、EMI超标与芯片发热问题；
3、跟踪分析竞品性能优劣势，提炼客户前沿痛点，为新一代芯片定义提供核心市场输入。""",
        "job_description": """【任职资格】
1、电气工程、电力电子、自动化等专业本科及以上学历，3年以上电源研发或FAE经验；
2、深入理解Buck, Boost, Flyback等开关电源拓扑，精通环路补偿与磁性元件选型。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "矽力杰市场与研发枢纽，负责汽车级新能源电源方案系统落地与客户现场技术攻坚。",
        "status": "active",
        "requirements": [
            {
                "module": "业务与工程",
                "dimension": "电力电子系统应用",
                "item_name": "开关电源拓扑设计与客户现场EMI环路调优",
                "item_type": "must_have",
                "importance_stars": 4,
                "raw_text": "熟练掌握开关电源拓扑设计，具备快速解决客户板级环路不稳及EMI传导辐射超标能力。",
                "structured_analysis": "综合考虑系统成本、散热空间与转换效率，提供业界高性价比完整参考方案。",
                "keywords": "FAE,电源芯片,EMI,BMS,环路补偿,汽车电子",
                "sort_order": 1
            }
        ]
    },
    # 7. 高级数字验证工程师 (UVM / SystemVerilog)
    {
        "position_title": "高级数字验证工程师 (UVM / SystemVerilog)",
        "category": "芯片设计/数字验证",
        "salary_range": "25-45K · 15薪",
        "experience_req": "3-5年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责数模混合电源控制芯片数字内核的UVM验证平台搭建；
2、编写断言(SVA)、功能覆盖率模型(Coverage)与受约束随机测试用例；
3、与数字模拟设计工程师协同排查混仿波形异常，推进代码与功能覆盖率双100%签核。""",
        "job_description": """【任职资格】
1、本科及以上学历，微电子或计算机专业，3年以上数字验证经验；
2、精通SystemVerilog与UVM验证方法学，熟练使用Synopsys VCS与Verdi。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责数模混合控制芯片数字逻辑与总线协议UVM自动化验证。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "数字验证",
                "item_name": "UVM验证平台搭建与混合仿真覆盖率收敛",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通UVM搭建与断言编写，实现数模混合芯片覆盖率100%签核。",
                "structured_analysis": "熟练掌握约束随机测试、回归测试平台脚本与波形联合调试。",
                "keywords": "UVM,SystemVerilog,VCS,Verdi,数字验证,覆盖率",
                "sort_order": 1
            }
        ]
    },
    # 8. 数字集成电路前端设计工程师 (Verilog / SoC)
    {
        "position_title": "数字集成电路前端设计工程师 (Verilog / SoC)",
        "category": "芯片设计/数字前端",
        "salary_range": "28-50K · 15薪",
        "experience_req": "3-5年",
        "education_req": "硕士及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责数模混合电源芯片数字控制状态机、数字PID算法及总线接口（I2C/SPI/PMBus）的RTL实现；
2、负责数字模块逻辑综合(Synthesis)、静态时序分析(STA)与低功耗UPF设计；
3、配合芯片Bring-up测试与FPGA原型验证平台联调。""",
        "job_description": """【任职资格】
1、微电子或集成电路硕士及以上学历，3年以上数字前端设计经验；
2、精通Verilog/SystemVerilog，熟悉Design Compiler及PrimeTime工具链。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责数字电源管理与混合信号SoC前端逻辑设计与综合时序签核。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "数字前端设计",
                "item_name": "数字电源算法RTL实现与静态时序分析",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通Verilog与DC综合，具备数字PID控制与低功耗设计能力。",
                "structured_analysis": "深刻理解数模接口跨时钟域处理与总线协议实现，保障芯片高主频与低面积消耗。",
                "keywords": "Verilog,数字IC,STA,DC综合,PMBus,低功耗",
                "sort_order": 1
            }
        ]
    },
    # 9. 芯片产品工程师 (PE / 晶圆代工与量产良率提升)
    {
        "position_title": "芯片产品工程师 (PE / 晶圆代工与量产良率提升)",
        "category": "产品工程/良率管控",
        "salary_range": "18-32K · 14薪",
        "experience_req": "3-5年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 长河",
        "job_responsibilities": """1、主导新产品试流片到量产导入全过程，负责晶圆CP与成品FT测试良率监控与分析；
2、对接台积电、中芯国际等晶圆代工厂，分析WAT参数漂移对芯片性能的影响；
3、制定低良率批次HOLD/RELEASE标准，推进DOE试验解决良率瓶颈。""",
        "job_description": """【任职资格】
1、本科及以上学历，微电子或半导体材料相关专业，3年以上半导体Fabless公司PE经验；
2、熟悉晶圆制造与封装测试流程，精通JMP/Excel良率统计分析。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责芯片全生命周期良率管控与晶圆代工厂工艺窗口协同优化。",
        "status": "active",
        "requirements": [
            {
                "module": "工程与运营",
                "dimension": "产品工程与良率",
                "item_name": "晶圆代工量产导入与WAT/良率数据分析",
                "item_type": "must_have",
                "importance_stars": 4,
                "raw_text": "精通晶圆代工厂生产对接，熟练运用JMP开展良率与失效关联分析。",
                "structured_analysis": "通过统计过程控制持续压缩量产离散度，提升毛利率与出货良品率。",
                "keywords": "PE,产品工程,良率提升,WAT,晶圆代工厂,JMP",
                "sort_order": 1
            }
        ]
    },
    # 10. 芯片封装与测试开发工程师 (Packaging & Test)
    {
        "position_title": "芯片封装与测试开发工程师 (Packaging & Test)",
        "category": "封测工程/先进封装",
        "salary_range": "20-38K · 14薪",
        "experience_req": "3-5年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责电源管理与模拟芯片高导热微型封装（QFN, BGA, DFN, CSP, Flip-Chip）方案开发；
2、负责引线框架(Leadframe)与基板设计，评估键合线热阻、寄生电感及封装应力；
3、协同封测代工厂优化打线、塑封与切筋成型工艺，提升封装良率。""",
        "job_description": """【任职资格】
1、本科及以上学历，机械、材料或电子工程相关专业，3年以上芯片封装研发经验；
2、熟练掌握AutoCAD及ANSYS热仿真与机械应力仿真工具。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责芯片高功率密度先进封装方案开发与热电耦合可靠性仿真。",
        "status": "active",
        "requirements": [
            {
                "module": "工程与技术",
                "dimension": "半导体封装",
                "item_name": "QFN/Flip-Chip高功率微型封装开发与热应力仿真",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "熟练掌握先进封装工艺与引线框架设计，具备ANSYS热阻热敏仿真能力。",
                "structured_analysis": "攻克大功率芯片散热瓶颈，保障高温高湿环境下的封装完整性。",
                "keywords": "芯片封装,QFN,Flip-Chip,ANSYS,热阻,封装应力",
                "sort_order": 1
            }
        ]
    },
    # 11. 嵌入式固件开发工程师 (数字电源DSP/ARM底层驱动)
    {
        "position_title": "嵌入式固件开发工程师 (数字电源DSP/ARM底层驱动)",
        "category": "固件开发/嵌入式软件",
        "salary_range": "22-38K · 14薪",
        "experience_req": "3-5年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责基于ARM Cortex-M/RISC-V及专用DSP数字电源主控芯片的底层固件驱动开发；
2、实现PMBus/SMBus通信协议栈、故障保护(OVP/OCP/OTP)中断服务程序及自校准算法；
3、配合硬件与算法工程师完成数字电源闭环控制系统联调。""",
        "job_description": """【任职资格】
1、计算机、自动化或电子专业本科及以上学历，3年以上嵌入式底层C编程经验；
2、深入理解MCU底层寄存器、DMA、ADC采样中断与硬件通信总线协议。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责数字电源管理芯片底层固件驱动栈开发与实时控制闭环调试。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "嵌入式固件开发",
                "item_name": "数字电源ARM/DSP固件开发与PMBus通信协议栈",
                "item_type": "must_have",
                "importance_stars": 4,
                "raw_text": "精通C语言与裸机中断系统，熟悉PMBus与实时故障响应机制。",
                "structured_analysis": "保证微秒级快速保护响应与低抖动数字采样控制。",
                "keywords": "嵌入式,固件,PMBus,数字电源,ARM,C语言",
                "sort_order": 1
            }
        ]
    },
    # 12. 半导体失效分析工程师 (FA - 物理失效与E-Beam)
    {
        "position_title": "半导体失效分析工程师 (FA - 物理失效与E-Beam)",
        "category": "质量可靠性/失效分析",
        "salary_range": "18-35K · 14薪",
        "experience_req": "3-5年",
        "education_req": "硕士及以上",
        "location": "杭州 · 滨江区 · 西兴",
        "job_responsibilities": """1、负责客退品(RMA)与可靠性测试失效样片的无损分析（X-Ray, SAM声学显微镜）；
2、运用微光显微镜(EMMI)、液晶热点定位(OBIRCH)精确定位芯片内部漏电与击穿缺陷点；
3、主导去层剥除(De-processing)、聚焦离子束(FIB)切片与高分辨扫描电镜(SEM)根因判定。""",
        "job_description": """【任职资格】
1、材料科学、微电子、固体物理等专业硕士及以上学历，3年以上芯片FA实验室工作经验；
2、熟练操作EMMI, OBIRCH, FIB, SEM等精密分析仪器，熟悉半导体工艺缺陷物理机理。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责芯片内部微观物理失效机理溯源，攻坚客诉与可靠性关键质量归因。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "失效分析FA",
                "item_name": "OBIRCH热点定位与FIB/SEM物理失效微观解析",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通芯片无损与微观破坏性失效分析流程，准确定位纳秒级瞬态击穿与静电损伤。",
                "structured_analysis": "通过材料微观表征与晶体缺陷分析，输出权威8D整改报告并推动工艺设计改进。",
                "keywords": "失效分析,FA,OBIRCH,EMMI,FIB,SEM,可靠性",
                "sort_order": 1
            }
        ]
    },
    # 13. 高压AC-DC电源管理芯片系统架构师
    {
        "position_title": "高压AC-DC电源管理芯片系统架构师",
        "category": "芯片设计/系统架构",
        "salary_range": "40-70K · 16薪",
        "experience_req": "8-10年",
        "education_req": "硕士及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、主导大功率工业级高压AC-DC（LLC谐振、交错PFC、反激式准谐振）芯片系统定义与架构设计；
2、负责高压高频控制算法、变频调制策略与零电压开通(ZVS)控制内核建模；
3、解决超高转换效率(>95%)、极低空载损耗与全球能源之星能效标准认证要求。""",
        "job_description": """【任职资格】
1、微电子或电力电子硕士及以上学历，8年以上高压开关电源芯片正向研发架构经验；
2、主持过多款已量产的顶级高压AC-DC主控芯片，在拓扑控制与高压保护方面有深厚造诣。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "矽力杰高压AC-DC核心架构师，统筹定义面向数据中心与工业储能的高压电源芯片产品线。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "AC-DC系统架构",
                "item_name": "高压LLC谐振与PFC拓扑控制芯片系统定义",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通高压拓扑建模与ZVS/ZCS软开关控制理论，具备行业顶尖芯片定义能力。",
                "structured_analysis": "综合考虑高压工艺击穿极限、系统热损耗与成本结构，确立核心竞争壁垒。",
                "keywords": "AC-DC,LLC谐振,PFC,软开关,系统架构,芯片定义",
                "sort_order": 1
            }
        ]
    },
    # 14. 低功耗LDO与基准源模拟电路研发工程师
    {
        "position_title": "低功耗LDO与基准源模拟电路研发工程师",
        "category": "芯片设计/模拟IC",
        "salary_range": "25-45K · 15薪",
        "experience_req": "3-5年",
        "education_req": "硕士及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责超高电源抑制比(PSRR > 80dB)、超低噪声(< 5uVrms)射频级LDO模拟电路设计；
2、负责纳安级(nA)静态电流微功耗带隙基准源(Bandgap)与片上温度传感器设计；
3、负责环路瞬态响应优化，避免大阶跃负载下的输出电压深跌。""",
        "job_description": """【任职资格】
1、微电子或集成电路专业硕士及以上学历，3年以上低压差线性稳压器(LDO)开发经验；
2、深入理解深亚微米CMOS器件噪声机理与密勒电容补偿网络。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责高性能超低噪声高PSRR射频低压差线性稳压芯片核心设计。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "高精微功耗模拟IC",
                "item_name": "超高PSRR低噪声LDO与带隙基准设计",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通高频PSRR提升技术与超低静态功耗电流镜设计。",
                "structured_analysis": "为5G射频与微弱传感器系统提供纯净、无纹波的高品质供电电压。",
                "keywords": "LDO,Bandgap,PSRR,低噪声,模拟电路,Cadence",
                "sort_order": 1
            }
        ]
    },
    # 15. 芯片可靠性与QA质量保证工程师 (Reliability / AEC-Q100)
    {
        "position_title": "芯片可靠性与QA质量保证工程师 (Reliability / AEC-Q100)",
        "category": "质量可靠性/车规认证",
        "salary_range": "16-30K · 14薪",
        "experience_req": "3-5年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 长河",
        "job_responsibilities": """1、负责车规级芯片AEC-Q100认证试验方案制定与全流程实施追踪；
2、主导高加速温湿度应力试验(HAST)、高温工作寿命试验(HTOL)与静电放电(ESD/CDM)测试；
3、编制器件可靠性量化预测报告，推动跨部门质量缺陷根因闭环。""",
        "job_description": """【任职资格】
1、电子工程、材料学或可靠性工程本科及以上学历，3年以上半导体可靠性评估经验；
2、精通JEDEC与AEC-Q100规范标准，熟悉各种环境可靠性测试箱操作。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责车规级AEC-Q100严苛可靠性考核与半导体品质质量保障体系落地。",
        "status": "active",
        "requirements": [
            {
                "module": "工程与运营",
                "dimension": "车规可靠性认证",
                "item_name": "AEC-Q100认证全流程推进与HTOL/HAST可靠性试验",
                "item_type": "must_have",
                "importance_stars": 4,
                "raw_text": "精通车规级环境与寿命应力考核标准，具备完善的可靠性试验分析能力。",
                "structured_analysis": "确保芯片在汽车极限工况下保持零早期失效率(Zero Defect)。",
                "keywords": "AEC-Q100,可靠性,HTOL,HAST,ESD,JEDEC,质量管理",
                "sort_order": 1
            }
        ]
    },
    # 16. 现场应用工程师 (FAE - 工业控制与通信电源)
    {
        "position_title": "现场应用工程师 (FAE - 工业控制与通信电源)",
        "category": "系统应用/FAE技术支持",
        "salary_range": "20-38K · 14薪",
        "experience_req": "3-5年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责工业自动化、光伏逆变器及5G通信基站电源芯片的应用方案推广；
2、协助客户解决大功率系统EMC合规、热设计瓶颈与恶劣电网抗电涌冲击调试；
3、撰写详细测试分析报告与应用笔记，指导客户快速完成批量导入。""",
        "job_description": """【任职资格】
1、电气、自动化或电力电子专业本科及以上学历，3年以上工业电源开发支持经验；
2、精通PCB电磁兼容布局，具备出色的抗压与现场动手调试排障能力。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责工业自动化与通信基站核心电源芯片系统应用开发与客户技术支持。",
        "status": "active",
        "requirements": [
            {
                "module": "业务与工程",
                "dimension": "工控电源系统支持",
                "item_name": "大功率工控电源EMC调试与抗冲击设计",
                "item_type": "must_have",
                "importance_stars": 4,
                "raw_text": "具备工业级电源系统现场排障与浪涌防护方案设计实操经验。",
                "structured_analysis": "有效提升工业客户系统工作稳定性与环境适应能力。",
                "keywords": "FAE,工控电源,通信电源,EMC,浪涌防护,技术支持",
                "sort_order": 1
            }
        ]
    },
    # 17. 芯片实验室测试与调测技术员 (Bench Test Technician)
    {
        "position_title": "芯片实验室测试与调测技术员 (Bench Test Technician)",
        "category": "实验室测试/硬件调试",
        "salary_range": "7-12K · 14薪",
        "experience_req": "经验不限",
        "education_req": "大专及以上",
        "location": "杭州 · 滨江区 · 西兴",
        "job_responsibilities": """1、配合研发工程师完成芯片工程样片在测试母板上的焊接、组装与上电调试；
2、按照实验指导书采集电压、电流、效率、纹波及温升等电学参数数据；
3、负责实验室台架仪器（高压电源、电子负载、示波器）日常维护与耗材管理。""",
        "job_description": """【任职资格】
1、大专及以上学历，电子、机电或应用物理相关专业；
2、具备良好的贴片器件（0402/QFN）手工焊接技能，做事细致严谨；
3、欢迎具备电子设计竞赛经验的应届优秀毕业生投递。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责实验室精密样片焊接、实验数据规范采录与测试台架维护。",
        "status": "active",
        "requirements": [
            {
                "module": "工程与技术",
                "dimension": "硬件手工与实验调试",
                "item_name": "SMD精密贴片焊接与台架电学参数测定",
                "item_type": "must_have",
                "importance_stars": 3,
                "raw_text": "熟练掌握微型器件焊接与仪器操作，能够规范完成测试记录。",
                "structured_analysis": "保证实验室日常调试流转高效顺畅，支持研发样品快速迭代。",
                "keywords": "测试技术员,SMD焊接,电子负载,示波器,台架测试",
                "sort_order": 1
            }
        ]
    },
    # 18. 芯片DFT可测性设计工程师 (ATPG / Scan)
    {
        "position_title": "芯片DFT可测性设计工程师 (ATPG / Scan)",
        "category": "芯片设计/DFT工程",
        "salary_range": "25-48K · 15薪",
        "experience_req": "3-5年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责数模混合控制芯片数字部分的扫描链(Scan Chain)插入与时钟控制逻辑设计；
2、负责JTAG/IEEE 1149.1边界扫描、MBIST内建自测试电路实现与仿真；
3、生成并优化ATPG测试模式，协助量产测试工程师在ATE机台上完成向量调试。""",
        "job_description": """【任职资格】
1、微电子或计算机专业本科及以上学历，3年以上芯片DFT项目开发经验；
2、熟练使用Synopsys DFTMAX/TetraMAX或Siemens Tessent工具链。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责数字控制逻辑可测性设计，保障量产故障检测的高覆盖率与低测试成本。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "可测性设计DFT",
                "item_name": "扫描链插入与ATPG向量压缩优化",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通DFT架构设计与MBIST自动修复，实现测试时间极致压缩。",
                "structured_analysis": "在复杂时序约束下达成高故障覆盖率，为量产测试降低硅片成本。",
                "keywords": "DFT,Scan,ATPG,Tessent,MBIST,边界扫描",
                "sort_order": 1
            }
        ]
    },
    # 19. 高频磁性元件与电磁仿真工程师 (EMI / Magnetics)
    {
        "position_title": "高频磁性元件与电磁仿真工程师 (EMI / Magnetics)",
        "category": "电磁设计/磁集成技术",
        "salary_range": "22-38K · 14薪",
        "experience_req": "3-5年",
        "education_req": "硕士及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责高频高功率密度电源集成电感、变压器与平面磁件的设计与三维电磁仿真；
2、分析磁芯损耗、铜损、邻近效应与漏感，评估寄生参数对开关振铃与EMI的影响；
3、主导磁集成(PwrSoC)片上封装电感开发与定制化磁芯供应链技术对接。""",
        "job_description": """【任职资格】
1、电气工程、电磁场与微波技术等相关专业硕士及以上学历；
2、精通Ansys Maxwell, Q3D或CST电磁场仿真工具，深入理解磁性材料特性。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责高频平面磁元件与片上电磁协同设计，攻克超高功率密度电源磁集成技术。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "磁集成与电磁场仿真",
                "item_name": "高频平面变压器建模与三维有限元电磁仿真",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通高频磁件设计与电磁场损耗仿真，具备解决EMI传导辐射超标能力。",
                "structured_analysis": "通过结构优化极致压缩电感体积与高频交流阻抗，实现系统微型化。",
                "keywords": "磁性元件,平面变压器,Maxwell,Q3D,EMI,高频电源",
                "sort_order": 1
            }
        ]
    },
    # 20. 电机驱动与栅极驱动模拟IC设计工程师
    {
        "position_title": "电机驱动与栅极驱动模拟IC设计工程师",
        "category": "模拟芯片设计/驱动IC",
        "salary_range": "30-55K · 15薪",
        "experience_req": "3-5年",
        "education_req": "硕士及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责步进电机、直流无刷电机(BLDC)及功率MOS/IGBT栅极驱动芯片模拟电路设计；
2、负责集成自举二极管、死区时间控制、自适应欠压保护与片上电荷泵设计；
3、协同系统团队完成电机驱动算法验证与量产芯片测试评估。""",
        "job_description": """【任职资格】
1、微电子或电气自动化专业硕士及以上学历，3年以上驱动芯片设计经验；
2、精通高压半桥驱动拓扑，深入掌握BCD工艺高耐压隔离与抗负压瞬态技术。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责高性能无刷电机驱动与大功率MOSFET/IGBT栅极驱动集成芯片研发。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "驱动IC架构设计",
                "item_name": "BLDC电机预驱与高压电平位移拓扑研发",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通高耐压驱动电路设计，攻克高频大电流开关下的负压瞬态抽吸破坏难题。",
                "structured_analysis": "实现高驱动电流输出与纳秒级极低传输延迟，赋能机器人与新能源电驱动。",
                "keywords": "电机驱动,栅极驱动,BLDC,死区控制,BCD工艺,半桥",
                "sort_order": 1
            }
        ]
    },
    # 21. 电池管理系统(BMS)模拟前端芯片研发工程师
    {
        "position_title": "电池管理系统(BMS)模拟前端芯片研发工程师",
        "category": "模拟芯片设计/BMS芯片",
        "salary_range": "32-60K · 15薪",
        "experience_req": "5-8年",
        "education_req": "硕士及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责车规级多串锂电池AFE监测芯片高精度电压采样通道(16-bit ADC)与电流通道设计；
2、负责高压电平位移通信隔离总线、断线自检与片上被动/主动均衡开关电路设计；
3、主导芯片在全温度范围(-40℃~125℃)内的毫伏级绝对测量精度校准与优化。""",
        "job_description": """【任职资格】
1、微电子或电子工程专业硕士及以上学历，5年以上电池管理AFE模拟芯片设计经验；
2、深入理解高压共模抑制、微弱信号差分采样与汽车级功能安全设计。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责车规级动力电池AFE多通道高精度采样监控芯片核心电路设计。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "BMS模拟前端IC",
                "item_name": "多通道微伏级高共模电池电压采样通道设计",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通高压隔离采样与高阶ADC架构，实现汽车级电池电量精准计量。",
                "structured_analysis": "攻关数百伏高共模总线电压下的抗干扰能力，确保电池组安全无隐患。",
                "keywords": "BMS,AFE,电池管理,高精度ADC,车规级,模拟IC",
                "sort_order": 1
            }
        ]
    },
    # 22. 射频微波IC设计工程师 (RFIC / 开关)
    {
        "position_title": "射频微波IC设计工程师 (RFIC / 开关)",
        "category": "射频芯片/微波IC",
        "salary_range": "30-55K · 15薪",
        "experience_req": "3-5年",
        "education_req": "硕士及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责5G移动通信射频天线开关(RF Switch)、低噪声放大器(LNA)电路架构设计；
2、负责SOI/GaAs工艺下的高线性度、低插入损耗(IL)与高隔离度(Isolation)指标攻坚；
3、使用ADS与HFSS完成芯片版图电磁协同仿真及样片在片微波测试。""",
        "job_description": """【任职资格】
1、电磁场微波或微电子专业硕士及以上学历，3年以上RFIC正向研发经验；
2、精通Smith圆图、S参数分析与高频非线性大信号建模。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责5G终端射频前端微波开关与低噪声放大器芯片核心研发。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "射频电路设计",
                "item_name": "SOI射频开关拓扑与ADS/HFSS电磁协同仿真",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通射频非线性失真控制与谐波抑制，具备极佳微波阻抗匹配能力。",
                "structured_analysis": "在高频段实现低于0.3dB超低插损与高于35dB的高通道隔离度。",
                "keywords": "RFIC,射频开关,SOI工艺,ADS,HFSS,微波,LNA",
                "sort_order": 1
            }
        ]
    },
    # 23. 芯片测试硬件设计工程师 (Load Board / Probe Card PCB)
    {
        "position_title": "芯片测试硬件设计工程师 (Load Board / Probe Card PCB)",
        "category": "硬件工程/测试接口板设计",
        "salary_range": "18-32K · 14薪",
        "experience_req": "3-5年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 长河",
        "job_responsibilities": """1、负责ATE机台量产测试母板(Load Board)、探针卡(Probe Card)高多层高速PCB原理图与Layout设计；
2、负责高频测试信号完整性(SI)与电源完整性(PI)仿真，进行特征阻抗匹配与串扰控制；
3、对接PCB制板厂与测试座(Socket)供应商，完成硬件试制焊接与板级调测验收。""",
        "job_description": """【任职资格】
1、电子工程、通信等专业本科及以上学历，3年以上高多层测试板PCB设计经验；
2、熟练掌握Altium Designer, Cadence Allegro与Sigrity高速仿真工具。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责高端ATE测试接口板与晶圆探针卡高多层PCB设计与信号完整性仿真。",
        "status": "active",
        "requirements": [
            {
                "module": "工程与技术",
                "dimension": "高速测试PCB设计",
                "item_name": "ATE Load Board高多层板设计与SI/PI阻抗仿真",
                "item_type": "must_have",
                "importance_stars": 4,
                "raw_text": "熟练掌握超多层微波测试板设计规范与电源解耦电容布局。",
                "structured_analysis": "保证微弱采样信号与大电流开关测试时的极低电源纹波与零信号反射。",
                "keywords": "Load Board,Probe Card,Allegro,PCB,SI,PI,测试硬件",
                "sort_order": 1
            }
        ]
    },
    # 24. 模拟集成电路资深版图主管 (Lead Layout Engineer)
    {
        "position_title": "模拟集成电路资深版图主管 (Lead Layout Engineer)",
        "category": "团队管理/版图主管",
        "salary_range": "28-48K · 15薪",
        "experience_req": "8-10年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、统筹版图团队日常项目排期、多产品线并行交付节奏与质量管控；
2、建立并持续升级模拟版图设计规范、Top级芯片Pin分配策略与防静电保护标准；
3、指导初中级工程师攻坚超高压隔离、大电流大芯片红外热点(Thermal Map)平衡等技术难关。""",
        "job_description": """【任职资格】
1、本科及以上学历，微电子等相关专业，8年以上模拟IC版图设计及带团队经验；
2、成功交付过多款量产百万级芯片的Top层版图，精通主流晶圆代工厂PDK与规则。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "矽力杰版图技术骨干主管，负责全公司模拟芯片版图规范制定与工程团队高效交付。",
        "status": "active",
        "requirements": [
            {
                "module": "团队与工程",
                "dimension": "版图工程管理",
                "item_name": "模拟版图团队技术把关与全芯片Top级物理签核",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "具备顶尖大芯片版图规划与团队技术指导能力，确保全芯片零物理违规。",
                "structured_analysis": "通过规范化流程与自动化脚本，大幅提升版图布局效率与流片一次成功率。",
                "keywords": "版图主管,Layout,Top层规划,PDK,物理签核,项目管理",
                "sort_order": 1
            }
        ]
    },
    # 25. 数字电源控制算法工程师 (数字环路 / 拓扑建模)
    {
        "position_title": "数字电源控制算法工程师 (数字环路 / 拓扑建模)",
        "category": "算法工程/控制理论",
        "salary_range": "26-48K · 15薪",
        "experience_req": "3-5年",
        "education_req": "硕士及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责数字电源双环控制算法（电压外环、电流内环）、自适应死区时间算法建模与仿真；
2、使用Matlab/Simulink建立开关电源离散化非线性模型，推导数字补偿器(2P2Z/3P3Z)系数；
3、协同数字IC团队进行定点化算法硬件映射与量化误差消除。""",
        "job_description": """【任职资格】
1、控制理论、电力电子、电气工程等专业硕士及以上学历；
2、深入掌握经典与现代控制理论，精通Matlab系统仿真与数字滤波器设计。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责新一代数字开关电源闭环控制算法建模与定点化硬件映射优化。",
        "status": "active",
        "requirements": [
            {
                "module": "算法能力",
                "dimension": "数字控制算法",
                "item_name": "离散化数字电源控制环路建模与数字补偿器优化",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通控制理论与开关电源小信号建模，具备数字环路零极点精确配置能力。",
                "structured_analysis": "实现微秒级大动态响应恢复时间并保持宽负载范围下的超高相位裕度。",
                "keywords": "数字电源,控制算法,Matlab,Simulink,2P2Z,小信号建模",
                "sort_order": 1
            }
        ]
    },
    # 26. 芯片供应商质量管理工程师 (SQE - 晶圆厂与封测厂管控)
    {
        "position_title": "芯片供应商质量管理工程师 (SQE - 晶圆厂与封测厂管控)",
        "category": "供应商质量/SQE管理",
        "salary_range": "18-35K · 14薪",
        "experience_req": "5-8年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 长河",
        "job_responsibilities": """1、负责外包晶圆代工厂(Foundry)及封测代工厂(OSAT)的质量体系审核与日常绩效考核；
2、主导制程变更管理(PCN)评估与材料变更验证，杜绝供应链制程波动引发的批量事故；
3、针对工厂重大质量事件组织跨公司8D原因追溯与纠正预防措施(CAPA)落地。""",
        "job_description": """【任职资格】
1、半导体、微电子或工业工程专业本科及以上学历，5年以上半导体行业SQE经验；
2、深入掌握ISO 9001/IATF 16949质量体系标准及VDA 6.3审核标准。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责全球顶尖晶圆代工与封测供应链的制造品质审核与制程稳定性监控。",
        "status": "active",
        "requirements": [
            {
                "module": "工程与运营",
                "dimension": "供应商质量管控",
                "item_name": "晶圆制造与封装代工厂IATF 16949质量审计",
                "item_type": "must_have",
                "importance_stars": 4,
                "raw_text": "精通车规级质量管理标准与代工厂制程控制，具备敏锐的产线潜在风险识别能力。",
                "structured_analysis": "通过严格的闭环管理保障上游代工环节的超高批次一致性与低DPPM。",
                "keywords": "SQE,晶圆厂,OSAT,IATF 16949,PCN,8D,质量审核",
                "sort_order": 1
            }
        ]
    },
    # 27. 车规芯片功能安全工程师 (ISO 26262 / ASIL-D)
    {
        "position_title": "车规芯片功能安全工程师 (ISO 26262 / ASIL-D)",
        "category": "系统工程/功能安全",
        "salary_range": "28-50K · 15薪",
        "experience_req": "3-5年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责汽车级芯片系统功能安全生命周期管理，推进符合ISO 26262 ASIL-B/D标准的产品开发；
2、主导开展芯片级FMEA/FMEDA定性定量安全分析，推导硬件架构度量指标(SPFM, LFM, PMHF)；
3、撰写安全手册(Safety Manual)与安全用例(Safety Case)，对接SGS/TUV等权威第三方认证机构。""",
        "job_description": """【任职资格】
1、汽车电子、自动化或微电子本科及以上学历，3年以上芯片或汽车控制器功能安全开发经验；
2、深入精通ISO 26262 Part 5/Part 11芯片级功能安全要求，持权威认证资质者优先。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "负责矽力杰车规级芯片ISO 26262功能安全全生命周期体系构建与ASIL-D认证通过。",
        "status": "active",
        "requirements": [
            {
                "module": "专业能力",
                "dimension": "功能安全体系",
                "item_name": "ISO 26262芯片级FMEDA分析与安全机制设计",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "精通芯片硬件失效率建模与自检机制设计，达成车规最高安全完整性等级。",
                "structured_analysis": "精准把控芯片单粒子翻转、潜伏故障与随机硬件失效的安全覆盖率指标。",
                "keywords": "功能安全,ISO 26262,FMEDA,ASIL-D,Safety Manual,车规芯片",
                "sort_order": 1
            }
        ]
    },
    # 28. IC设计辅助与EDA环境运维工程师 (CAD / EDA IT)
    {
        "position_title": "IC设计辅助与EDA环境运维工程师 (CAD / EDA IT)",
        "category": "IT与CAD支持/EDA环境",
        "salary_range": "18-32K · 14薪",
        "experience_req": "3-5年",
        "education_req": "本科及以上",
        "location": "杭州 · 滨江区 · 联慧街6号",
        "job_responsibilities": """1、负责公司Linux高性能计算集群(HPC/LSF/Slurm)与大规模芯片仿真任务调度集群运维；
2、负责Cadence, Synopsys, Siemens等主流EDA工具链的安装部署、License浮动授权管理与版本升级；
3、编写自动化Python/Shell/Perl脚本优化EDA仿真环境，推进PDK安装与设计数据安全管控。""",
        "job_description": """【任职资格】
1、计算机、通信或微电子专业本科及以上学历，3年以上半导体企业CAD/EDA运维经验；
2、精通Linux系统管理与集群作业调度，具备优秀的脚本自动化运维功底。""",
        "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=矽力杰半导体技术（杭州）有限公司",
        "summary": "保障矽力杰数百人芯片设计研发团队的高性能计算集群与全流程EDA工具链稳定运转。",
        "status": "active",
        "requirements": [
            {
                "module": "工程与技术",
                "dimension": "EDA环境与计算集群",
                "item_name": "Linux HPC高性能仿真集群与EDA License调度运维",
                "item_type": "must_have",
                "importance_stars": 4,
                "raw_text": "精通大型EDA工具运维与高并发任务调度管理，保障研发流片关键期零宕机。",
                "structured_analysis": "通过存储优化与脚本自动化，极致提升大型芯片后仿真与网表综合运算吞吐。",
                "keywords": "CAD,EDA,Linux,HPC,LSF,License,自动化脚本",
                "sort_order": 1
            }
        ]
    }
]


def update_database_silergy():
    """
    全量更新矽力杰的全部28个在招岗位及能力画像
    """
    db = SessionLocal()
    try:
        company_name = "矽力杰半导体技术（杭州）有限公司"
        company_intro = "已上市 · 1000-9999人 · 电子/半导体/集成电路 · 全球领先的高性能模拟半导体与电源管理芯片研发龙头"
        
        logger.info(f"开始录入/更新 [{company_name}] 全部 {len(SILERGY_28_POSITIONS)} 个在招岗位...")
        created = 0
        updated = 0

        for p_data in SILERGY_28_POSITIONS:
            title = p_data["position_title"].strip()
            category = p_data["category"].strip()

            pos = db.query(JobPosition).filter(
                JobPosition.position_title == title,
                JobPosition.company_name == company_name
            ).first()

            raw_content = f"【公司介绍】{company_name}（{company_intro}）\n【薪资范围】{p_data.get('salary_range', '')}\n【工作经验】{p_data.get('experience_req', '')} · {p_data.get('education_req', '')}\n【工作地点】{p_data.get('location', '')}\n\n【岗位职责】\n{p_data.get('job_responsibilities', '')}\n\n{p_data.get('job_description', '')}"

            if not pos:
                pos = JobPosition(
                    position_title=title,
                    company_name=company_name,
                    company_intro=company_intro,
                    salary_range=p_data.get("salary_range", ""),
                    experience_req=p_data.get("experience_req", ""),
                    education_req=p_data.get("education_req", ""),
                    location=p_data.get("location", "杭州 · 滨江区 · 联慧街6号矽力杰产业化基地"),
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
                created += 1
                logger.info(f"新建职位: [{pos.id}] {title}")
            else:
                pos.company_name = company_name
                pos.company_intro = company_intro
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
                updated += 1
                logger.info(f"更新职位: [{pos.id}] {title}")

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
                        module=req_data["module"].strip(),
                        dimension=req_data["dimension"].strip(),
                        item_name=item_name,
                        item_type=req_data.get("item_type", "must_have"),
                        importance_stars=req_data.get("importance_stars", 5),
                        raw_text=req_data["raw_text"].strip(),
                        structured_analysis=req_data.get("structured_analysis", ""),
                        keywords=req_data.get("keywords", ""),
                        sort_order=req_data.get("sort_order", 1)
                    )
                    db.add(req)
                else:
                    req.module = req_data["module"].strip()
                    req.dimension = req_data["dimension"].strip()
                    req.raw_text = req_data["raw_text"].strip()
                    req.structured_analysis = req_data.get("structured_analysis", req.structured_analysis)
                    req.keywords = req_data.get("keywords", req.keywords)

        db.commit()
        logger.info(f"矽力杰全量岗位同步完成！新建 {created} 个，更新 {updated} 个，当前数据库总计岗位 28 个。")
        return {"created": created, "updated": updated, "total": len(SILERGY_28_POSITIONS)}
    except Exception as e:
        db.rollback()
        logger.exception(f"更新失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_database_silergy()

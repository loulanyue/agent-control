#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
半导体重点企业岗位权威字典 - 第三部分
涵盖 装备制造（求是、昂坤）、特种与功率（地芯引力、芯迈、航芯源、博思芯宇、城芯、硅新、芯港、国科微、中芯国际、华虹等）
"""

from typing import Dict, Any

def create_requirement(module: str, dimension: str, item_name: str, item_type: str, stars: int, raw_text: str, analysis: str, keywords: str, sort_order: int = 1):
    return {
        "module": module,
        "dimension": dimension,
        "item_name": item_name,
        "item_type": item_type,
        "importance_stars": stars,
        "raw_text": raw_text,
        "structured_analysis": analysis,
        "keywords": keywords,
        "sort_order": sort_order
    }

SEMI_COMPANIES_PART3_REGISTRY: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # 16. 浙江求是半导体设备有限公司 & 浙江求是创芯半导体设备有限公司 (半导体核心装备)
    # -------------------------------------------------------------------------
    "浙江求是半导体设备有限公司": {
        "company_name": "浙江求是半导体设备有限公司",
        "company_intro": "浙大孵化/高精尖装备 · 100-499人 · 半导体设备/装备制造 · 致力于集成电路制造前道超洁净单晶圆湿法清洗与化学刻蚀装备自研",
        "location_default": "杭州 · 滨江区 / 萧山区",
        "positions": [
            {
                "position_title": "半导体超洁净微流体化学清洗系统研发工程师",
                "category": "半导体装备/流体机械",
                "salary_range": "20-38K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 萧山区",
                "job_responsibilities": """1、负责12英寸晶圆单片湿法清洗机台微流体喷淋管路、化学药液精确定量配比系统设计；
2、使用Fluent开展气液两相流动力学仿真，优化晶圆表面兆声波(Megasonic)清洗空化气泡均匀度；
3、解决强腐蚀性化学药液（氢氟酸/王水）在超高洁净度要求下的零金属析出与密封防泄漏设计。""",
                "job_description": """【任职资格】
1、机械工程、流体机械或流体动力学专业本科及以上学历，3年以上半导体湿法设备研发经验；
2、熟悉PFA/PTFE特氟龙微管道焊接与无颗粒残留隔膜阀控制。""",
                "source_image": "https://www.zhipin.com/gongsi/job/qiushi-eq.html",
                "summary": "研发12英寸单晶圆高洁净湿法清洗装备微流体分配机构与兆声波气泡清洗技术。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "半导体流体装备", "兆声波气液两相流清洗与耐强酸氟塑料管路设计", "must_have", 5,
                                       "熟练运用Fluent仿真晶圆高速旋转下的化学液边界层膜厚分布与表面颗粒脱附动力学。",
                                       "深入掌握半导体级超高纯PFA流体元件装配规范，确保机台金属离子溶出达到ppt级控制要求。",
                                       "半导体装备,湿法清洗,Fluent仿真,流体机械,兆声波", 1)
                ]
            }
        ]
    },

    "浙江求是创芯半导体设备有限公司": {
        "company_name": "浙江求是创芯半导体设备有限公司",
        "company_intro": "高精尖装备 · 100-499人 · 半导体设备/集成制造 · 专注于高端集成电路刻蚀与薄膜沉积装备关键零部件与精密机台研发",
        "location_default": "杭州 · 萧山区",
        "positions": [
            {
                "position_title": "半导体等离子体射频电源与阻抗匹配器研发专家",
                "category": "半导体装备/射频电气",
                "salary_range": "28-48K · 15薪",
                "experience_req": "5-8年",
                "education_req": "硕士及以上",
                "location": "杭州 · 萧山区",
                "job_responsibilities": """1、负责半导体刻蚀机与PECVD机台13.56MHz / 2MHz高功率脉冲射频电源及自动阻抗匹配网络(Match Box)研发；
2、设计高速动态可变真空电容伺服驱动调谐算法，实现毫秒级等离子体起辉阻抗匹配；
3、抑制等离子体负载突变导致的反射功率冲击，保护高压射频功率管安全工作。""",
                "job_description": """【任职资格】
1、电力电子、射频微波或电气工程专业硕士及以上学历，5年以上等离子体高频射频电源研发经验；
2、精通高频大功率逆变拓扑与微波传输线阻抗圆图(Smith Chart)调配理论。""",
                "source_image": "https://www.zhipin.com/gongsi/job/qiushi-chuangxin.html",
                "summary": "攻关半导体前道干法刻蚀装备核心零部件——千瓦级精密脉冲射频电源与动态阻抗匹配箱。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "射频电源匹配", "13.56MHz等离子体自动匹配箱与Smith圆图阻抗动态锁定", "must_have", 5,
                                       "精通利用DSP/FPGA实现高频相位幅度检相与反射系数动态极小值快速梯度搜索算法。",
                                       "掌握高电压大电流射频电感铜管水冷散热与微波电磁屏蔽设计规范。",
                                       "射频电源,匹配箱,等离子体,刻蚀机,Smith圆图,半导体装备", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 17. 杭州昂坤半导体设备有限公司 (半导体纳米级光学缺陷检测装备)
    # -------------------------------------------------------------------------
    "杭州昂坤半导体设备有限公司": {
        "company_name": "杭州昂坤半导体设备有限公司",
        "company_intro": "国家高新技术/隐形冠军 · 100-499人 · 半导体设备/精密光学 · 专注于半导体晶圆前道宏观与微观纳米级光学缺陷检测设备国产化替代",
        "location_default": "杭州 · 钱塘区 · 医药港小镇 / 大江东",
        "positions": [
            {
                "position_title": "半导体光学系统设计高级工程师 (明场/暗场大视场光学)",
                "category": "半导体装备/光学系统",
                "salary_range": "25-45K · 14薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 钱塘区",
                "job_responsibilities": """1、负责半导体晶圆微观纳米缺陷检测大视场(FOV)、大数值孔径(NA > 0.8)明场与暗场物镜成像光路设计；
2、使用Zemax / Code V优化光学系统波像差、色差与畸变，实现衍射极限分辨率成像；
3、负责超宽光谱DUV深紫外激光照明光源与高精度显微物镜镜头组装调测。""",
                "job_description": """【任职资格】
1、光学工程、光电仪器专业硕士及以上学历，3年以上精密显微光学系统设计经验；
2、熟悉干涉仪测量物镜波前误差与精密光学公差敏感度分析。""",
                "source_image": "https://www.zhipin.com/gongsi/job/angkun.html",
                "summary": "负责晶圆微纳米缺陷检测大孔径超分辨显微光学物镜与激光暗场散射成像光路设计。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "光学系统设计", "高NA显微物镜消色差设计与波前像差Zemax优化", "must_have", 5,
                                       "熟练运用Zemax进行多组元透镜公差分配与蒙特卡洛公差良率分析，指导装配工艺。",
                                       "掌握暗场微弱散射光收集椭球面反射镜设计，极大提升纳米级颗粒缺陷信噪比。",
                                       "光学设计,Zemax,显微物镜,缺陷检测,半导体设备,明暗场", 1)
                ]
            },
            {
                "position_title": "半导体晶圆微纳米缺陷图像深度学习识别算法工程师",
                "category": "算法工程/计算机视觉",
                "salary_range": "28-50K · 14薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 钱塘区",
                "job_responsibilities": """1、负责晶圆高速线扫(TDI)成像微米/纳米级缺陷（划伤、微颗粒、图形断线、残胶）特征提取与分类算法研发；
2、针对极度不平衡的小样本工业缺陷，构建基于自监督学习与少样本迁移的缺陷分类模型；
3、将深度学习推理模型在GPU/TensorRT端进行毫秒级高吞吐实时并发部署。""",
                "job_description": """【任职资格】
1、计算机视觉、模式识别、自动化专业硕士及以上学历，3年以上半导体或工业AOI缺陷检测算法经验；
2、精通PyTorch及TensorRT模型加速，熟悉典型晶圆宏微观缺陷形貌特征。""",
                "source_image": "https://www.zhipin.com/gongsi/job/angkun.html",
                "summary": "研发基于深度学习的晶圆表面亚微米微观缺陷毫秒级在线自动识别与归类算法。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "视觉算法", "小样本晶圆微缺陷自动分类(ADC)与TensorRT实时推理", "must_have", 5,
                                       "熟练运用图像差分(Die-to-Die)、自适应阈值分割融合深度目标检测模型提取弱对比度缺陷。",
                                       "精通利用CUDA与TensorRT实现高分辨率千兆像素/秒图像数据流的实时低延迟推理。",
                                       "计算机视觉,缺陷检测,AOI,TensorRT,PyTorch,小样本学习", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 18. 浙江地芯引力科技有限公司 (5G射频前端与快充芯片)
    # -------------------------------------------------------------------------
    "浙江地芯引力科技有限公司": {
        "company_name": "浙江地芯引力科技有限公司",
        "company_intro": "高新技术企业 · 100-499人 · 芯片设计/射频混合 · 专注于移动通信射频前端芯片与智能快充电源管理芯片研发",
        "location_default": "杭州 · 滨江区 · 长河街道",
        "positions": [
            {
                "position_title": "5G射频功率放大器(PA)设计工程师 (GaAs / CMOS)",
                "category": "芯片设计/射频IC",
                "salary_range": "30-55K · 14薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责Sub-6GHz 5G移动终端高能效射频功率放大器(PA)电路设计；
2、负责高饱和输出功率(Psat)、高功率附加效率(PAE)与低线性度失真(ACLR)拓扑优化；
3、设计片上差分驱动放大级与紧凑型多层低温共烧陶瓷(LTCC)微型输出匹配网络。""",
                "job_description": """【任职资格】
1、电磁场与微波技术、微电子专业硕士及以上学历，3年以上射频PA正向开发经验；
2、熟练掌握Keysight ADS及Cadence SpectreRF，深入理解GaAs HBT与SOI CMOS射频工艺。""",
                "source_image": "https://www.zhipin.com/gongsi/job/dixinyinli.html",
                "summary": "研发5G终端高效率射频功率放大器芯片核心电路与封装级微波匹配网络。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "射频PA设计", "5G射频功率放大器效率PAE与ACLR线性度权衡设计", "must_have", 5,
                                       "精通利用数字预失真(DPD)与包络跟踪(ET)架构提升射频PA在大峰均比信号下的回退效率。",
                                       "具备精确匹配键合引线寄生电感与层间互感耦合微波仿真的实战经验。",
                                       "射频PA,5G,GaAs,ADS仿真,微波技术,功率放大器", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 19. 芯迈半导体技术（杭州）股份有限公司 (功率器件与模拟器件)
    # -------------------------------------------------------------------------
    "芯迈半导体技术（杭州）股份有限公司": {
        "company_name": "芯迈半导体技术（杭州）股份有限公司",
        "company_intro": "拟上市/专精特新 · 100-499人 · 芯片设计/功率器件 · 专注于超结MOSFET、第三代半导体SiC/GaN与高性能功率驱动研发",
        "location_default": "杭州 · 滨江区 · 浦沿街道",
        "positions": [
            {
                "position_title": "中高压超结MOSFET器件开发工程师",
                "category": "器件研发/功率半导体",
                "salary_range": "25-45K · 14薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责650V/800V高密度超结MOSFET (Super Junction) 器件结构设计与电荷平衡(Charge Balance)设计；
2、运用Synopsys Sentaurus TCAD进行多层外延或深槽刻蚀填充工艺仿真，优化导通电阻Rsp；
3、主导晶圆流片后器件静态击穿耐压(BV)、雪崩耐量(EAS)与反向恢复电荷(Qrr)特性测试评测。""",
                "job_description": """【任职资格】
1、微电子学、固体物理或半导体材料专业硕士及以上学历，3年以上超结MOSFET正向设计经验；
2、精通高压器件电场调制原理，熟悉深槽刻蚀与高深宽比外延填充制造工艺。""",
                "source_image": "https://www.zhipin.com/gongsi/job/xinmai.html",
                "summary": "研发打破硅极限比导通电阻的高压超结功率MOSFET器件结构与高雪崩击穿耐量技术。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "功率器件设计", "超结MOSFET电荷严格平衡与TCAD工艺电学仿真", "must_have", 5,
                                       "精通P柱与N柱杂质浓度精密电荷平衡条件分析，拓宽制造容差窗口与耐压BV裕度。",
                                       "具备设计集成快恢复二极管(FRD)结构以大幅降低体二极管反向恢复损耗的工程经验。",
                                       "超结MOSFET,Super Junction,TCAD,功率半导体,Sentaurus,EAS", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 20. 杭州城芯科技有限公司 (SoC设计服务与定制芯片)
    # -------------------------------------------------------------------------
    "杭州城芯科技有限公司": {
        "company_name": "杭州城芯科技有限公司",
        "company_intro": "高新技术企业 · 100-499人 · 芯片设计服务 · 提供从规格定义到量产交付的一站式定制SoC与先进IP集成设计服务",
        "location_default": "杭州 · 滨江区",
        "positions": [
            {
                "position_title": "芯片物理设计后端工程师 (APR / P&R)",
                "category": "芯片设计/后端实现",
                "salary_range": "22-40K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责28nm/22nm及以下制程复杂SoC芯片的布局布线(Floorplan/P&R)与电源网络规划；
2、主导时钟树综合(CTS)、拥塞消除及静态时序分析(STA)时序违例修复；
3、完成物理规则检查(DRC/LVS)清零与流片GDSII数据交付导出。""",
                "job_description": """【任职资格】
1、微电子或集成电路相关专业本科及以上学历，3年以上芯片物理设计后端经验；
2、熟练掌握Innovus或ICC2，熟练编写Tcl脚本进行批处理。""",
                "source_image": "https://www.zhipin.com/gongsi/job/chengxin.html",
                "summary": "负责一站式SoC定制芯片后端物理设计布局布线与时序全面收敛签核。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "后端物理设计", "复杂SoC电源环网规划与先进制程CTS时钟树搭建", "must_have", 4,
                                       "精通多电压域低功耗UPF物理隔离实现与电源开关单胞(Power Switch)阵列布局。",
                                       "具备快速排除局部高密度布线拥塞热点与天线效应(Antenna)修剪的实战技能。",
                                       "APR,Innovus,STA,CTS,P&R,物理设计", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 21. 浙江航芯源集成电路科技有限公司 (特种高可靠集成电路)
    # -------------------------------------------------------------------------
    "浙江航芯源集成电路科技有限公司": {
        "company_name": "浙江航芯源集成电路科技有限公司",
        "company_intro": "军民融合/特种高科技 · 100-499人 · 芯片设计/高可靠特种 · 专注于航天、航空及工业特种领域高可靠、抗辐射加固集成电路设计",
        "location_default": "杭州 · 滨江区",
        "positions": [
            {
                "position_title": "特种宇航级陶瓷与金属气密封装工艺工程师",
                "category": "封测工程/特种封装",
                "salary_range": "20-38K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责军工宇航级多层陶瓷封装(CQFP/CLCC)及金属气密外壳封装工艺开发；
2、主导金丝/铝丝超声楔形键合(Wedge Bonding)、平行缝焊(Seam Welding)气密封焊工艺调测；
3、执行严苛的高温储存、机械冲击、粒子碰撞噪声检测(PIND)及细检漏(氦质谱)/粗检漏可靠性试验。""",
                "job_description": """【任职资格】
1、材料工程、电子封装或精密机械专业本科及以上学历，3年以上高可靠特种封装经验；
2、熟悉GJB 548B微电子器件试验方法与航天特种气密封装规范。""",
                "source_image": "https://www.zhipin.com/gongsi/job/hangxinyuan.html",
                "summary": "设计满足深空探测与特种装备极值极端工况的金属陶瓷全气密高可靠芯片封装方案。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "特种气密封装", "氦质谱微漏率检测与真空平行缝焊工艺参数控制", "must_have", 5,
                                       "精通封焊保护气氛水氧含量控制(<100ppm)，保证腔体内部气氛长期防氧化与防腐蚀。",
                                       "掌握金丝键合拉力测试与剪切力标准，有效杜绝微观焊点开裂虚焊重大隐患。",
                                       "气密封装,缝焊,PIND,氦质谱检漏,GJB548B,特种芯片", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 22. 杭州士兰集成电路有限公司 (士兰微晶圆制造基地)
    # -------------------------------------------------------------------------
    "杭州士兰集成电路有限公司": {
        "company_name": "杭州士兰集成电路有限公司",
        "company_intro": "上市公司全资基地 · 1000-9999人 · 晶圆制造/半导体 · 士兰微电子旗下集双极、BiCMOS与高压功率器件规模化制造的现代化芯片制造基地",
        "location_default": "杭州 · 钱塘区 · 下沙经济技术开发区",
        "positions": [
            {
                "position_title": "半导体制造核心设备维修与点检工程师",
                "category": "设备工程/半导体设备",
                "salary_range": "15-28K · 14薪",
                "experience_req": "3-5年",
                "education_req": "大专及以上",
                "location": "杭州 · 钱塘区 · 下沙",
                "job_responsibilities": """1、负责扩散炉管、离子注入机、化学气相沉积(CVD)等前道机台机械运动臂与真空腔体维修保养；
2、解决机台真空气路泄漏、温度温控热电偶漂移及传送晶圆(Robot)抓取打滑碎片故障；
3、执行日常点检与备品备件耗材寿命管理，降低设备故障非计划停机时间(MTTR)。""",
                "job_description": """【任职资格】
1、机电一体化、机械电气或半导体自动化专业大专及以上学历，3年以上晶圆制造设备维修经验；
2、熟悉干泵、分子泵等真空获得设备工作原理，具备扎实的机械电气排障能力。""",
                "source_image": "https://www.zhipin.com/gongsi/job/silan-ic.html",
                "summary": "负责保障前道晶圆制造生产线关键工艺机台高真空度、高精度温控与不间断连续产出。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "设备点检维修", "真空腔体检漏与半导体机械臂超净晶圆传送对中调试", "must_have", 4,
                                       "熟练运用氦质谱检漏仪排查高真空密封法兰微漏点，保障工艺腔体真空度达到微托级指标。",
                                       "精通机械手示教编程与零位标定，彻底消除晶圆传输划伤与碎片风险。",
                                       "设备维修,真空机台,扩散炉,机械臂,晶圆制造,点检", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 23. 中芯国际集成电路制造有限公司 (晶圆代工巨头)
    # -------------------------------------------------------------------------
    "中芯国际集成电路制造有限公司": {
        "company_name": "中芯国际集成电路制造有限公司",
        "company_intro": "已上市 · 10000人以上 · 半导体晶圆代工 · 中国大陆规模最大、技术最先进的集成电路制造晶圆代工龙头企业",
        "location_default": "全国 / 杭州业务基地",
        "positions": [
            {
                "position_title": "14nm/28nm先进工艺节点工艺整合工程师 (PIE)",
                "category": "晶圆制造/工艺整合",
                "salary_range": "30-55K · 15薪",
                "experience_req": "5-8年",
                "education_req": "硕士及以上",
                "location": "杭州 / 生产基地",
                "job_responsibilities": """1、负责先进FinFET / HKMG工艺节点全流程集成方案优化与良率提升攻坚；
2、协同光刻、刻蚀、薄膜等模块攻坚栅极漏电、接触电阻过高及侧墙微结构缺陷；
3、分析先进制程WAT电学参数正态分布，优化器件速度与功耗(PPA)工艺裕量。""",
                "job_description": """【任职资格】
1、微电子科学与工程、凝聚态物理相关专业硕士及以上学历，5年以上先进制程晶圆代工厂PIE经验；
2、精通FinFET三维多栅器件物理机理与短沟道效应抑制对策。""",
                "source_image": "https://www.zhipin.com/gongsi/job/smic.html",
                "summary": "负责先进制程节点工艺整合与三维FinFET晶体管微观结构漏电良率系统性提升。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "先进制程PIE", "FinFET工艺整合与WAT电学性能良率攻坚", "must_have", 5,
                                       "掌握高介电常数金属栅(HKMG)热预算分配与源漏应变硅(SiGe)外延接触电阻优化工艺。",
                                       "具备将微观TEM切片形貌缺陷与宏观WAT电参数偏离进行精准关联映射的深厚经验。",
                                       "PIE,FinFET,中芯国际,工艺整合,WAT,先进制程", 1)
                ]
            },
            {
                "position_title": "光刻工艺高级工程师 (ASML浸没式ArFi光刻)",
                "category": "晶圆制造/光刻工艺",
                "salary_range": "28-48K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 / 生产基地",
                "job_responsibilities": """1、负责193nm浸没式(ArFi)光刻机工艺窗口研发与超细线宽极紫外辅助曝光；
2、优化浸润流体气泡控制、超高折射率保护层(Topcoat)涂胶与离轴照明(OAI)瞳面照明配方；
3、解决极限线宽下的线边缘粗糙度(LER)与纳米级套刻误差(Overlay < 3nm)。""",
                "job_description": """【任职资格】
1、光学、微电子、化学工程专业硕士及以上学历，3年以上浸没式光刻机台工艺经验；
2、精通ASML Twinscan NXT浸没式光刻系统操作与计算光刻OPC修正反馈。""",
                "source_image": "https://www.zhipin.com/gongsi/job/smic.html",
                "summary": "负责浸没式光刻机台深紫外纳米级细微线条曝光工艺开发与套刻精度闭环签核。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "ArFi浸没式光刻", "浸没式水膜流场控制与超高精度套刻Overlay消除", "must_have", 5,
                                       "精通离轴照明瞳面优化与相移掩模(PSM)配合，极大拓宽亚波长光刻焦深(DOF)工艺裕量。",
                                       "掌握流体水痕缺陷(Watermark)消除机制与浸没式浸润头防污染工艺控制。",
                                       "光刻,ArFi,ASML,Overlay,浸没式光刻,先进制程", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 24. 华虹半导体有限公司 (特色工艺晶圆代工巨头)
    # -------------------------------------------------------------------------
    "华虹半导体有限公司": {
        "company_name": "华虹半导体有限公司",
        "company_intro": "已上市 · 10000人以上 · 半导体晶圆代工 · 全球领先的特色工艺晶圆代工龙头，深耕嵌入式非易失性存储器与功率器件",
        "location_default": "全国 / 杭州业务基地",
        "positions": [
            {
                "position_title": "汽车级BCD电源管理晶圆工艺整合工程师",
                "category": "晶圆制造/工艺整合",
                "salary_range": "26-45K · 15薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 / 生产基地",
                "job_responsibilities": """1、负责车规级BCD (Bipolar-CMOS-DMOS) 模拟特色工艺平台新产品流片与工艺整合；
2、主导解决车规AEC-Q100认证中出现的高温反偏(HTRB)击穿电压早期退化缺陷；
3、优化隔离槽深度与高压漂移区注入剂量，降低芯片导通电阻并增强抗寄生可控硅闩锁(Latch-up)能力。""",
                "job_description": """【任职资格】
1、微电子、材料科学相关专业本科及以上学历，3年以上高压BCD工艺整合实战经验；
2、熟悉车载芯片零缺陷(Zero Defect)管理理念与IATF 16949质量工具。""",
                "source_image": "https://www.zhipin.com/gongsi/job/hhgrace.html",
                "summary": "负责华虹特色车规高可靠BCD电源管理工艺平台整合与超高耐压击穿良率优化。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "车规BCD工艺", "高压结隔离与高温反偏HTRB可靠性缺陷改善", "must_have", 5,
                                       "掌握深沟槽隔离(DTI)与高阻硅外延技术在车规大功率驱动芯片中的抑制串扰应用。",
                                       "熟练编写流片Split Plan试验方案，针对客户定制化耐压规格快速微调工艺窗口。",
                                       "BCD工艺,车规晶圆,PIE,华虹半导体,DTI,高压器件", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 25. 杭州国科微电子有限公司 (机器视觉/车载/固态存储芯片)
    # -------------------------------------------------------------------------
    "杭州国科微电子有限公司": {
        "company_name": "杭州国科微电子有限公司",
        "company_intro": "已上市子公司 · 500-999人 · 芯片设计 · 聚焦超高清视频编解码、智能机器视觉ISP及固态存储主控芯片研发",
        "location_default": "杭州 · 滨江区",
        "positions": [
            {
                "position_title": "ISP图像信号处理器架构与调优算法工程师",
                "category": "算法工程/图像处理",
                "salary_range": "25-45K · 14薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责自研车载与安防监控芯片硬件ISP流水线架构设计与画质调优；
2、负责高动态范围(HDR)多曝光合成、3D数字降噪(3DNR)与自动白平衡(AWB)算法硬件化；
3、使用专业测试卡与光源箱标定摄像头Sensor噪点模型与色彩还原矩阵。""",
                "job_description": """【任职资格】
1、信号与信息处理、计算机科学专业硕士及以上学历，3年以上ISP流水线算法设计经验；
2、熟悉CMOS图像传感器工作特性与色彩科学。""",
                "source_image": "https://www.zhipin.com/gongsi/job/goke.html",
                "summary": "研发高端智能视觉ISP图像处理硬件流水线核心算子与极端照度成像画质调优。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "ISP图像调优", "多帧HDR合成与3D数字降噪硬件化算法设计", "must_have", 5,
                                       "熟练掌握暗光高噪点下的空域时域滤波算法，平衡运动伪影与画面边缘锐度细节。",
                                       "精通Imatest软件分析MTF清晰度、色彩饱和度及暗角补偿曲线。",
                                       "ISP,HDR,3DNR,CMOS Sensor,图像调优,计算机视觉", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 26. 杭州博思芯宇科技有限公司 (存储与微电子研发)
    # -------------------------------------------------------------------------
    "杭州博思芯宇科技有限公司": {
        "company_name": "杭州博思芯宇科技有限公司",
        "company_intro": "高新技术 · 100-499人 · 芯片设计/存储器 · 专注于移动智能终端NAND Flash控制与固态存储固件架构研发",
        "location_default": "杭州 · 滨江区",
        "positions": [
            {
                "position_title": "固态存储LDPC纠错算法研发工程师",
                "category": "算法工程/存储算法",
                "salary_range": "28-50K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责3D NAND闪存主控芯片硬件LDPC码译码器算法架构设计与定点仿真；
2、设计软判决(Soft Decision)与硬判决(Hard Decision)动态切换译码策略，延长闪存P/E寿命；
3、协同数字前端工程师将译码流水线在低延时低门数限制下高效实现。""",
                "job_description": """【任职资格】
1、信息论与编码、通信或数学专业硕士及以上学历，3年以上存储或通信LDPC纠错算法经验；
2、熟练掌握C/C++及MATLAB仿真，深入理解信道误码特性。""",
                "source_image": "https://www.zhipin.com/gongsi/job/broadex.html",
                "summary": "研发先进高吞吐低延迟LDPC纠错译码引擎，突破高密度3D QLC闪存读写寿命极限。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "信道纠错编码", "高吞吐分层准循环QC-LDPC最小和(Min-Sum)译码优化", "must_have", 5,
                                       "精通基于信噪比变化的LLR对数似然比动态表更新与误码平层(Error Floor)抑制策略。",
                                       "熟练进行固定字长截断与量化误差仿真，保证硬件译码吞吐量超过GB/s门槛。",
                                       "LDPC,3D NAND,纠错算法,闪存主控,信息论,数字设计", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 27. 芯扬聚阵（杭州）微电子有限公司 (毫米波雷达与射频前端)
    # -------------------------------------------------------------------------
    "芯扬聚阵（杭州）微电子有限公司": {
        "company_name": "芯扬聚阵（杭州）微电子有限公司",
        "company_intro": "高新技术 · 100-499人 · 芯片设计/毫米波射频 · 专注于77GHz/79GHz车载高精度毫米波雷达单片收发机芯片研发",
        "location_default": "杭州 · 钱塘区",
        "positions": [
            {
                "position_title": "77GHz车载毫米波雷达单片收发机模拟IC设计工程师",
                "category": "芯片设计/毫米波IC",
                "salary_range": "32-60K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 钱塘区",
                "job_responsibilities": """1、负责77GHz/79GHz FMCW车载毫米波雷达单片收发机(Transceiver)微波单片集成电路(MMIC)正向设计；
2、负责77GHz压控振荡器(VCO)、移相器(Phase Shifter)、低噪声功率放大器及IQ混频器设计；
3、主导芯片在探针台高频波导接口与毫米波暗室中的辐射方向图与测距测角精度测试。""",
                "job_description": """【任职资格】
1、电磁场与微波技术、微电子专业硕士及以上学历，3年以上毫米波集成电路正向研发经验；
2、精通高频工艺（SiGe或CMOS）寄生提取与片上微带线/共面波导高频电磁场仿真。""",
                "source_image": "https://www.zhipin.com/gongsi/job/xinyang.html",
                "summary": "研发智能汽车高阶自动驾驶核心77GHz毫米波雷达单片全集成收发机芯片。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "毫米波MMIC设计", "77GHz超低相噪VCO与宽频带移相器单片集成设计", "must_have", 5,
                                       "熟练运用HFSS对片上高频传输线、十字交叉连线进行全波电磁场仿真与阻抗匹配。",
                                       "掌握FMCW雷达线性调频连续波啁啾(Chirp)斜率线性度高精度校准技术。",
                                       "毫米波雷达,77GHz,MMIC,VCO,HFSS,射频IC", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 28. 杭州硅新人工智能科技有限公司 (存算一体AI芯片)
    # -------------------------------------------------------------------------
    "杭州硅新人工智能科技有限公司": {
        "company_name": "杭州硅新人工智能科技有限公司",
        "company_intro": "前沿硬科技 · 100-499人 · 芯片设计/存算一体 · 突破冯·诺依曼架构内存墙瓶颈的新型存内计算(Computing-in-Memory)芯片创新企业",
        "location_default": "杭州 · 滨江区",
        "positions": [
            {
                "position_title": "模拟阻变存储器(RRAM)/SRAM存算一体宏单元电路设计工程师",
                "category": "芯片设计/存算一体",
                "salary_range": "30-58K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责基于SRAM/RRAM的存内模拟矩阵乘累加(MAC)宏单元(CIM Macro)电路设计；
2、负责高精度电流模/电荷模累加器、低功耗高转换速率SAR ADC及自适应失调校准逻辑；
3、解决模拟存内计算在不同工艺、电压、温度(PVT)变化下的计算精度漂移问题。""",
                "job_description": """【任职资格】
1、微电子、集成电路专业硕士及以上学历，3年以上存算一体或存储器模拟电路设计经验；
2、熟悉模拟计算信噪比理论与阵列非理想性补偿技术。""",
                "source_image": "https://www.zhipin.com/gongsi/job/guixin.html",
                "summary": "研发突破内存墙的新型SRAM/RRAM存算一体计算宏单元，实现超百TOPS/W极致能效比。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "存算一体设计", "模拟电荷模MAC阵列与低功耗Flash/SAR ADC接口设计", "must_have", 5,
                                       "深刻掌握基尔霍夫电流定律阵列并行累加中的非线性压降(IR-Drop)与器件电导漂移补偿方案。",
                                       "具备根据神经网络量化容错特性设计高鲁棒性存算电路架构的跨层优化能力。",
                                       "存算一体,CIM,RRAM,SRAM,低功耗,模拟计算", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 29. 杭州芯港智能科技有限公司 (智能传感器芯片与MEMS集成)
    # -------------------------------------------------------------------------
    "杭州芯港智能科技有限公司": {
        "company_name": "杭州芯港智能科技有限公司",
        "company_intro": "高新技术 · 100-499人 · 芯片设计/传感器 · 专注于智能传感器调理芯片(AFE)与高精度MEMS多传感器微系统研发",
        "location_default": "杭州 · 钱塘区",
        "positions": [
            {
                "position_title": "传感器微弱信号检测调理专用集成电路(ASIC)设计工程师",
                "category": "芯片设计/模拟前端",
                "salary_range": "25-45K · 14薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 钱塘区",
                "job_responsibilities": """1、负责电容式、压阻式MEMS传感器接口读出调理芯片(AFE)模拟电路设计；
2、设计微伏级仪表放大器(INA)、自稳零斩波器、电容-电压(C/V)转换电路及片上温度传感器；
3、主导芯片流片后与MEMS敏感芯片的合封系统联调与全温区零点漂移校正。""",
                "job_description": """【任职资格】
1、微电子科学、电路与系统专业硕士及以上学历，3年以上微弱信号模拟前端设计经验；
2、深入理解运算放大器微弱电荷积分与1/f低频噪声优化。""",
                "source_image": "https://www.zhipin.com/gongsi/job/xingang.html",
                "summary": "设计高灵敏度MEMS传感器专用模拟读出芯片，实现纳伏级电平信号精密放大与温漂抑制。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "传感器调理AFE", "开关电容C/V转换放大器与仪表运放失调动态消除", "must_have", 5,
                                       "掌握双相关采样(CDS)与斩波技术抑制低频噪声，实现飞法级(fF)微小电容变化的高线性检测。",
                                       "熟练进行多项式温度补偿算法与片上EEPROM存储多点校准逻辑协同设计。",
                                       "传感器AFE,MEMS读出,仪表放大器,低噪声,模拟IC,C/V转换", 1)
                ]
            }
        ]
    }
}

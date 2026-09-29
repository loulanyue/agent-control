#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
半导体重点企业岗位权威字典 - 第二部分
涵盖 芯昇电子、国芯微、积海半导体、士兰集昕、士兰集成、芯云半导体、创芯集成电路、行芯科技、华芯巨数、晶华微等
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

SEMI_COMPANIES_PART2_REGISTRY: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # 7. 浙江芯昇电子技术有限公司 (中移物联网自研芯片龙头)
    # -------------------------------------------------------------------------
    "浙江芯昇电子技术有限公司": {
        "company_name": "浙江芯昇电子技术有限公司",
        "company_intro": "央企控股/中国移动旗下 · 500-999人 · 芯片设计/物联网芯片 · 聚焦RISC-V物联网MCU、安全芯片与蜂窝通信射频芯片研发",
        "location_default": "杭州 · 余杭区 · 未来科技城",
        "positions": [
            {
                "position_title": "物联网安全MCU芯片系统架构师 (国密商密二级安全)",
                "category": "芯片设计/系统架构",
                "salary_range": "35-58K · 15薪",
                "experience_req": "5-8年",
                "education_req": "硕士及以上",
                "location": "杭州 · 余杭区 · 未来科技城",
                "job_responsibilities": """1、负责自研物联网安全MCU芯片的系统架构设计，制定CPU内核、总线互联及存储子系统拓扑；
2、主导国密SM2/SM3/SM4硬件加速引擎、物理防克隆PUF、防侧信道攻击(DPA)硬件安全屏障设计；
3、推动芯片获得商用密码产品认证二级及EAL4+安全认证。""",
                "job_description": """【任职资格】
1、微电子、信息安全或计算机体系结构专业硕士及以上学历，5年以上安全芯片架构设计经验；
2、深入理解ARM TrustZone或RISC-V安全扩展，精通侧信道攻击防护与硬件故障注入检测机制。""",
                "source_image": "https://www.zhipin.com/gongsi/job/cmcc-chip.html",
                "summary": "研发中移物联网国家级安全MCU芯片系统架构，构筑万物互联硬件级安全底座。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "安全芯片架构", "国密硬件加速与抗侧信道攻击(DPA)架构设计", "must_have", 5,
                                       "熟练设计SM4动态密钥混淆与硬件掩码算法，防御差分功耗分析与电磁泄露攻击。",
                                       "精通安全引导(Secure Boot)、硬件信任根(Root of Trust)与调试接口加密锁定机制。",
                                       "安全MCU,国密算法,DPA防护,RISC-V,PUF,系统架构", 1)
                ]
            },
            {
                "position_title": "低功耗蜂窝通信RF射频前端研发工程师 (Cat.1 / NB-IoT)",
                "category": "芯片设计/射频IC",
                "salary_range": "28-48K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 余杭区 · 未来科技城",
                "job_responsibilities": """1、负责Cat.1 / NB-IoT多模蜂窝物联网收发机(Transceiver)射频前端模拟电路设计；
2、负责低噪声放大器(LNA)、下混频器(Mixer)、可变增益放大器(VGA)及射频频率合成器(PLL/VCO)设计；
3、主导射频流片后在矢量网络分析仪与综合测试仪上的灵敏度与邻道抑制比验证。""",
                "job_description": """【任职资格】
1、微波技术与电磁场、微电子专业硕士及以上学历，3年以上蜂窝通信射频前端正向设计经验；
2、精通Cadence SpectreRF / ADS设计工具，熟悉CMOS/SOI工艺射频器件高频建模。""",
                "source_image": "https://www.zhipin.com/gongsi/job/cmcc-chip.html",
                "summary": "负责超低功耗蜂窝物联网通信射频收发芯片模拟前端正向设计与流片调测。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "射频前端电路", "CMOS低噪声放大器与低相位噪声VCO电路设计", "must_have", 5,
                                       "精通低偏置电流下的射频增益与噪声系数(NF)优化平衡，实现极限灵敏度达标。",
                                       "掌握片上片外LC阻抗匹配与高次谐波滤波设计，满足3GPP通信发射杂散指标。",
                                       "射频IC,Cat.1,NB-IoT,LNA,VCO,Cadence,SpectreRF", 1)
                ]
            },
            {
                "position_title": "现场应用支持工程师 (FAE - 智能表计与工业物联网)",
                "category": "技术支持/FAE",
                "salary_range": "16-30K · 14薪",
                "experience_req": "1-3年",
                "education_req": "本科及以上",
                "location": "杭州 · 余杭区 · 未来科技城",
                "job_responsibilities": """1、负责国家电网、南方电网智能电表及水气热表计客户的MCU方案选型与技术对接；
2、协同客户排查板级超低功耗待机漏电、RTC时钟温漂及ESD静电打坏等工程问题；
3、编制典型行业SDK软硬件应用例程，加速大客户量产导入周期。""",
                "job_description": """【任职资格】
1、自动化、仪器仪表或电子信息专业本科及以上学历，2年以上智能表计或物联网FAE经验；
2、熟悉单片机低功耗模式切换与锂电池供电系统的功耗优化分析。""",
                "source_image": "https://www.zhipin.com/gongsi/job/cmcc-chip.html",
                "summary": "推进自研低功耗MCU在智能电网表计与工业数采终端的大规模商用落地与现场攻坚。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "低功耗调试", "物联网终端微安级低功耗电流捕获与RTC精度补偿", "must_have", 4,
                                       "熟练运用高精度微电流测量仪抓取芯片休眠与唤醒瞬态波形，精准排查外设漏电节点。",
                                       "熟悉表计DL/T 645与CJ/T 188协议栈，具备在MCU裸机或RTOS上的快速移植调试能力。",
                                       "FAE,智能表计,低功耗,MCU,RTC校准,现场调试", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 8. 杭州国芯微电子股份有限公司 (数字音视频/AIOT/语音NPU芯片设计上市龙头)
    # -------------------------------------------------------------------------
    "杭州国芯微电子股份有限公司": {
        "company_name": "杭州国芯微电子股份有限公司",
        "company_intro": "拟上市/行业龙头 · 500-999人 · 芯片设计/人工智能 · 国内领先的机顶盒芯片与端侧AI语音交互SoC芯片领军企业",
        "location_default": "杭州 · 西湖区 · 文三路 / 古墩路",
        "positions": [
            {
                "position_title": "智能语音低功耗NPU芯片微架构设计工程师",
                "category": "芯片设计/AI芯片",
                "salary_range": "30-55K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 西湖区 · 古墩路",
                "job_responsibilities": """1、负责端侧超低功耗唤醒词检测(KWS)与语音降噪专用神经网络NPU计算核微架构设计；
2、设计支持8-bit/4-bit整型量化矩阵乘累加(MAC)阵列与片上环形缓冲区缓存管理逻辑；
3、运用Verilog完成RTL编写，通过仿真验证确保在毫瓦级功耗下提供充足算力。""",
                "job_description": """【任职资格】
1、微电子、信号与信息处理专业硕士及以上学历，3年以上专用硬件加速器设计经验；
2、熟悉语音前端降噪算法（Beamforming/AEC）与离线轻量级神经网络结构。""",
                "source_image": "https://www.zhipin.com/gongsi/job/nationalchip.html",
                "summary": "研发国芯微自主毫瓦级超低功耗端侧AI语音识别与波束成形加速计算核心。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "NPU计算微架构", "低比特量化矩阵计算核与低漏电功耗关断控制", "must_have", 5,
                                       "掌握基于活动检测(VAD)的多级休眠门控时钟(Clock Gating)与电源切断微架构优化。",
                                       "精通利用定点数仿真分析神经网络权重截断误差，实现算法模型与硬件算子的无缝拟合。",
                                       "NPU,AI语音,微架构,低功耗,量化计算,Verilog", 1)
                ]
            },
            {
                "position_title": "高精度低噪声音频Codec模拟电路设计工程师",
                "category": "芯片设计/模拟IC",
                "salary_range": "28-48K · 14薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 西湖区 · 古墩路",
                "job_responsibilities": """1、负责多通道高动态范围音频ADC/DAC、低噪声麦克风前置放大器(PGA)模拟电路设计；
2、负责音频锁相环(Audio PLL)、高电源抑制比(PSRR) LDO及防爆破音(Pop-noise)抑制电路设计；
3、主导流片后在音频分析仪(Audio Precision APx555)上的信噪比(SNR)与THD+N实测调优。""",
                "job_description": """【任职资格】
1、微电子、电子工程专业硕士及以上学历，3年以上音频模拟Codec或高精度Sigma-Delta ADC设计经验；
2、深入理解开关电容电路、差分放大器闪烁噪声(1/f噪声)与斩波调制(Chopper)技术。""",
                "source_image": "https://www.zhipin.com/gongsi/job/nationalchip.html",
                "summary": "设计超高保真音频编解码芯片模拟前端，攻坚微伏级输入噪声抑制与100dB+信噪比。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "音频模拟设计", "斩波稳零放大器与高动态范围Sigma-Delta调制器设计", "must_have", 5,
                                       "精通斩波技术消除运放1/f粉红噪声与输入失调电压，优化麦克风小信号捕捉灵敏度。",
                                       "熟练运用APx555音频分析仪定位晶圆测试中的谐波失真与基频串扰来源。",
                                       "音频Codec,ADC,DAC,APx555,斩波技术,模拟IC", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 9. 杭州积海半导体有限公司 (12英寸集成电路制造)
    # -------------------------------------------------------------------------
    "杭州积海半导体有限公司": {
        "company_name": "杭州积海半导体有限公司",
        "company_intro": "国资参股龙头 · 1000-9999人 · 半导体晶圆制造 · 杭州重点打造的先进12英寸特色工艺集成电路晶圆制造产业化基地",
        "location_default": "杭州 · 钱塘区 · 大江东临江高新技术产业园区",
        "positions": [
            {
                "position_title": "晶圆厂CIM/MES智能制造架构师 (半导体车间自动化控制)",
                "category": "软件工程/CIM系统",
                "salary_range": "30-50K · 15薪",
                "experience_req": "5-8年",
                "education_req": "本科及以上",
                "location": "杭州 · 钱塘区 · 大江东",
                "job_responsibilities": """1、负责12英寸晶圆厂全自动化制造执行系统MES、智能调度Dispatching及AMHS天车物流调度系统集成架构；
2、设计基于SECS/GEM及EDA标准的万台级机台毫秒级设备数据采集与实时SPC报警分析平台；
3、保障晶圆厂7x24小时全流程无人化高可用自动化连续生产运行。""",
                "job_description": """【任职资格】
1、计算机、软件或自动化工程专业本科及以上学历，5年以上12英寸大型晶圆厂CIM核心架构研发经验；
2、精通半导体制造全工序生产流转模型，熟悉IBM SiView、Applied Materials FAB300等主流CIM套件。""",
                "source_image": "https://www.zhipin.com/gongsi/job/jihai.html",
                "summary": "负责12英寸晶圆工厂核心智能制造CIM/MES系统架构设计与高可用无故障保障。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "晶圆CIM架构", "12英寸AMHS天车物流与MES动态自动化派工架构", "must_have", 5,
                                       "精通跨机台瓶颈调度算法与晶圆Q-Time工艺防呆拦截控制，最大化提升全厂机台产出稼动率(OEE)。",
                                       "熟练构建高吞吐分布式消息队列与高可用双活数据库集群，防范系统宕机导致的批次报废。",
                                       "CIM,MES,AMHS,SECS/GEM,智能制造,晶圆厂", 1)
                ]
            },
            {
                "position_title": "晶圆厂安全环保与特气防灾高级工程师 (EHS)",
                "category": "质量与安全/EHS",
                "salary_range": "18-32K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 钱塘区 · 大江东",
                "job_responsibilities": """1、负责晶圆厂硅烷(SiH4)、三氟化氮(NF3)、砷烷等剧毒自燃易爆化学特气的全生命周期安全监控与防灾体系维护；
2、主导含氟废水处理站、有机废气燃烧洗涤塔(Scrubber/RTO)等环保设施合规运行达标；
3、组织全厂防泄漏应急演练，推进ISO 14001环境管理与ISO 45001职业健康安全认证。""",
                "job_description": """【任职资格】
1、安全工程、环境工程或化学工程专业本科及以上学历，3年以上晶圆制造半导体厂EHS工作经验；
2、持有注册安全工程师资格证书，熟悉半导体特种气体泄漏传感联锁与防爆电气规范。""",
                "source_image": "https://www.zhipin.com/gongsi/job/jihai.html",
                "summary": "严守12英寸洁净室生命线，负责易燃有毒半导体特气管网防灾与环保减排闭环。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "特气防灾与环保", "剧毒自燃半导体特气联锁监控与废气废液达标处理", "must_have", 4,
                                       "精通晶圆厂毒性自燃气体监测系统(TGMS)与紧急切断阀(ESV)双重冗余逻辑测试及巡检。",
                                       "熟练掌握酸性废气洗涤、高浓度氨氮与含氟蚀刻废液絮凝沉淀无害化工艺调优。",
                                       "EHS,半导体特气,环保,TGMS,洗涤塔,晶圆厂", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 10. 杭州士兰集昕微电子有限公司 (士兰微8/12英寸特色晶圆基地)
    # -------------------------------------------------------------------------
    "杭州士兰集昕微电子有限公司": {
        "company_name": "杭州士兰集昕微电子有限公司",
        "company_intro": "上市公司全资子公司 · 1000-9999人 · 晶圆制造/半导体 · 士兰微电子旗下高压BCD与特色工艺核心晶圆制造生产基地",
        "location_default": "杭州 · 钱塘区 · 大江东产业集聚区",
        "positions": [
            {
                "position_title": "8英寸高压BCD特色工艺整合工程师 (PIE)",
                "category": "晶圆制造/工艺整合",
                "salary_range": "25-42K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 钱塘区 · 大江东",
                "job_responsibilities": """1、负责700V高压BCD工艺、超结MOSFET工艺平台的工艺窗口集成与良率爬坡；
2、统筹光刻、刻蚀、注入、高温热氧化等各模块工序交互作用，解决耐压击穿与漏电(Ioff)缺陷；
3、主导晶圆流片打件试验、设计规则(DRC Rule)确认与工艺可靠性验证。""",
                "job_description": """【任职资格】
1、微电子、集成电路相关专业本科及以上学历，3年以上特色工艺晶圆厂PIE实操经验；
2、深刻理解高压器件结终端技术、双扩散金属氧化物(DMOS)结构物理机理。""",
                "source_image": "https://www.zhipin.com/gongsi/job/silan-jixin.html",
                "summary": "负责高压BCD及功率半导体特色工艺全流程工艺整合与高压击穿良率攻坚。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "BCD工艺整合", "高压结终端耐压匹配与隔离槽工艺缺陷调优", "must_have", 5,
                                       "熟练分析横向双扩散高压MOS器件漂移区掺杂浓度与击穿耐压(BV)敏感度曲线。",
                                       "具备运用TCAD工艺仿真协同分析工艺波动对器件阈值电压与导通电阻影响的综合能力。",
                                       "PIE,BCD工艺,高压器件,工艺整合,良率爬坡,晶圆制造", 1)
                ]
            },
            {
                "position_title": "光刻机台设备维护工程师 (ASML / 尼康步进机)",
                "category": "设备工程/光刻维护",
                "salary_range": "18-32K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 钱塘区 · 大江东",
                "job_responsibilities": """1、负责ASML PAS5500 / Nikon Stepper光刻机台日常预防性维护(PM)、精度校准与故障抢修；
2、调试激光干涉仪定位系统、物镜镜头热漂移校正及掩模版台(Reticle Stage)纳米级运动对准；
3、分析机台套刻对准误差(Overlay Error)，确保晶圆层间套准偏差在工艺容差以内。""",
                "job_description": """【任职资格】
1、机械工程、精密仪器、自动化或测控专业本科及以上学历，3年以上半导体光刻设备维护经验；
2、熟悉光刻机内部光学照明系统、气浮导轨及高精度伺服电机结构。""",
                "source_image": "https://www.zhipin.com/gongsi/job/silan-jixin.html",
                "summary": "负责先进制程生命机台——光刻机纳米级超精密运动机构与光学投影透镜校准维护。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "光刻机台维保", "ASML光刻机套刻对准精度校准与激光干涉定位调测", "must_have", 4,
                                       "熟练运用机器视觉与光学对准标识分析套刻残差分布，独立排除机械微卡死故障。",
                                       "严格遵循无尘洁净室防尘作业标准，安全执行机台激光光源更替与光学镜片防污染清洁。",
                                       "设备工程师,光刻机,ASML,Nikon,Overlay,精密仪器", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 11. 杭州芯云半导体集团有限公司 (第三方高端芯片封测与测试服务龙头)
    # -------------------------------------------------------------------------
    "杭州芯云半导体集团有限公司": {
        "company_name": "杭州芯云半导体集团有限公司",
        "company_intro": "行业领军 · 500-999人 · 芯片测试/封测服务 · 国内高等级一站式集成电路晶圆测试与芯片成品测试独立第三方龙头",
        "location_default": "杭州 · 萧山区 / 钱塘区",
        "positions": [
            {
                "position_title": "高端SoC测试程序开发工程师 (Advantest V93000)",
                "category": "芯片测试/ATE",
                "salary_range": "25-45K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 萧山区",
                "job_responsibilities": """1、负责基于爱德万Advantest V93000 (Smarticle/Dragon)平台的多核SoC数字芯片测试程序开发；
2、利用SmarTest软件将设计团队的STIL/WGL仿真向量无损转化并映射到机台波形时序；
3、优化Scan测试、BIST测试及高速接口(USB/PCIe)测试时间，实现多Site高吞吐测试。""",
                "job_description": """【任职资格】
1、微电子、通信工程或测控技术专业本科及以上学历，3年以上V93000机台实战开发经验；
2、熟练掌握C++/Python测试编程，熟悉数字芯片DFT原理与故障模型。""",
                "source_image": "https://www.zhipin.com/gongsi/job/xinyun.html",
                "summary": "负责多核复杂SoC及汽车电子芯片在V93000旗舰机台的高速批量量产测试程序开发。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "V93000测试开发", "SmarTest测试向量转换与千兆引脚高速数字时序调试", "must_have", 5,
                                       "熟练编写测试程序精确定位Scan Chain扫描链断链与Memory BIST修复故障位。",
                                       "掌握测试机台引脚通道阻抗匹配与高频抖动标定，保障百万级芯片量产测试一致性。",
                                       "V93000,Advantest,SoC测试,SmarTest,Scan测试,ATE", 1)
                ]
            },
            {
                "position_title": "晶圆探针卡(Probe Card)及高频测试板(Loadboard)硬件设计工程师",
                "category": "硬件研发/测试硬件",
                "salary_range": "20-35K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 萧山区",
                "job_responsibilities": """1、负责超百层高密度ATE测试板(Load Board)与垂直微弹簧探针卡(Probe Card)硬件原理图与PCB Layout设计；
2、进行高速信号差分阻抗控制(100Ω±5%)、电源层PDN阻抗去耦仿真及回流路径优化；
3、对接探针卡制造商，评估探针针尖共面度、扎针压力及高低温变形可靠性。""",
                "job_description": """【任职资格】
1、电子工程、电磁场与微波专业本科及以上学历，3年以上高频高速PCB或探针卡设计经验；
2、熟练使用Cadence Allegro与Ansys SIwave / HFSS电磁仿真软件。""",
                "source_image": "https://www.zhipin.com/gongsi/job/xinyun.html",
                "summary": "设计高频高速芯片测试接口板卡与纳米级精密垂直探针卡硬件硬件电路。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "测试硬件设计", "超高层Loadboard信号完整性仿真与探针卡微间距走线", "must_have", 5,
                                       "精通利用HFSS对测试插座(Socket)及微探针进行三维高频电磁场寄生参数建模。",
                                       "熟练规划数十组电源轨低阻抗去耦电容网络，将测试板电源瞬态纹波抑制在mV级以内。",
                                       "Probe Card,Loadboard,PCB设计,SIwave,HFSS,信号完整性", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 12. 浙江创芯集成电路有限公司 (12英寸先进封测平台)
    # -------------------------------------------------------------------------
    "浙江创芯集成电路有限公司": {
        "company_name": "浙江创芯集成电路有限公司",
        "company_intro": "科研院所孵化/高科技 · 100-499人 · 芯片研发/特色制造 · 依托浙江大学杭州国际科创中心打造的先进特色工艺与高端封装研发平台",
        "location_default": "杭州 · 萧山区 · 建设三路",
        "positions": [
            {
                "position_title": "先进晶圆级封装工艺工程师 (WLCSP / Fan-out)",
                "category": "封测工程/先进封装",
                "salary_range": "25-42K · 14薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 萧山区",
                "job_responsibilities": """1、主导晶圆级芯片封装(WLCSP)及扇出型晶圆级封装(Fan-out WLP)工艺方案开发；
2、优化聚酰亚胺(PI)介质层光刻固化、再布线层(RDL)电镀铜线宽线距(L/S < 2/2μm)工艺；
3、解决重构晶圆(Reconstituted Wafer)成型中的环氧塑封料(EMC)翘曲(Warpage)与芯片位移(Die Shift)。""",
                "job_description": """【任职资格】
1、材料物理、微电子、化学工程专业硕士及以上学历，3年以上先进封装工艺研发经验；
2、熟悉重布线RDL电镀、凸块(Bumping)及晶圆减薄划片全工艺流程。""",
                "source_image": "https://www.zhipin.com/gongsi/job/chuangxin.html",
                "summary": "研发先进扇出型微米级超密重布线RDL与极薄晶圆微凸块互连封装工艺。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "先进晶圆级封装", "高密度RDL细线宽电镀与晶圆翘曲应力控制", "must_have", 5,
                                       "精通利用有限元仿真分析不同热膨胀系数(CTE)材料在热循环中的应力集中点。",
                                       "掌握亚微米光刻对准技术，有效消除高长宽比微通孔电镀填充空洞与界面分层缺陷。",
                                       "先进封装,WLCSP,Fan-out,RDL,翘曲控制,晶圆级封装", 1)
                ]
            },
            {
                "position_title": "TSV硅通孔与微凸块(Micro-bump)工艺研发工程师",
                "category": "封测工程/3D集成",
                "salary_range": "28-48K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 萧山区",
                "job_responsibilities": """1、负责2.5D/3D Chiplet异构集成中深硅通孔(TSV)蚀刻、介质绝缘层沉积及金属铜无缝电镀填充；
2、研发节距(Pitch)小于30μm的高密度微凸块(Micro-bump)倒装焊(Flip-Chip)精密键合工艺；
3、利用超声扫描显微镜(CSAM)与X-Ray检测界面微空洞与冷焊虚焊缺陷。""",
                "job_description": """【任职资格】
1、微电子、电子封装工程专业硕士及以上学历，3年以上TSV或三维多芯片集成研发经验；
2、熟悉BOSCH深硅刻蚀工艺机理与铜互扩散热处理退火窗口。""",
                "source_image": "https://www.zhipin.com/gongsi/job/chuangxin.html",
                "summary": "攻关3D Chiplet先进异质异构集成核心——超深TSV硅通孔纳米级无孔洞金属填充。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "3D异构集成", "高深宽比TSV无盲孔电镀填充与超细间距Micro-bump键合", "must_have", 5,
                                       "熟练掌握电镀液添加剂配比对深孔底向上(Bottom-up)电镀超填充动力学机制的调控。",
                                       "具备高精度倒装热压键合(TCB)参数设计与焊料界面金属间化合物(IMC)厚度控制技能。",
                                       "TSV,3D集成,Chiplet,Micro-bump,微凸块,先进封装", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 13. 杭州行芯科技有限公司 (国产EDA物理签核与RC寄生参数提取龙头)
    # -------------------------------------------------------------------------
    "杭州行芯科技有限公司": {
        "company_name": "杭州行芯科技有限公司",
        "company_intro": "高新技术/专精特新 · 100-499人 · 芯片EDA软件 · 国内EDA物理设计签核与全芯片高精度寄生参数提取软件研发领航者",
        "location_default": "杭州 · 滨江区 · 聚工路",
        "positions": [
            {
                "position_title": "EDA时序分析(STA)与时钟树分析核心算法工程师",
                "category": "EDA软件/核心算法",
                "salary_range": "30-60K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责全芯片静态时序分析(STA)引擎核心算法研发，实现图遍历(Graph-based)与路径搜索；
2、实现高级片上偏差(AOCV)与参数化片上偏差(POCV)时序反标与悲观度消除(CRPR)算法；
3、攻坚先进制程纳米节点多工艺角(Multi-Corner Multi-Mode)下大规模时序图并行求解加速。""",
                "job_description": """【任职资格】
1、计算机科学、运筹学或微电子专业硕士及以上学历，3年以上EDA时序签核算法开发实操经验；
2、精通现代C++ (C++17/20)、超大规模有向无环图(DAG)遍历优化与内存紧凑型数据结构。""",
                "source_image": "https://www.zhipin.com/gongsi/job/phy-eda.html",
                "summary": "研发国产自主高性能静态时序分析EDA签核引擎，攻克先进制程千亿级拓扑时序求解。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "EDA核心算法", "POCV统计时序分析算法与CRPR悲观度快速消除", "must_have", 5,
                                       "精通基于图论的高性能拓扑排序、最长/最短路径增量分析算法，具备极高代码执行效率。",
                                       "熟悉Liberty时序模型与先进制程物理效应，确保时序计算结果与业界标杆工具绝对收敛。",
                                       "EDA,STA,时序分析,POCV,C++,算法开发", 1)
                ]
            },
            {
                "position_title": "EDA产品测试与应用工程师 (AE - 晶圆厂PDK验证)",
                "category": "技术支持/AE",
                "salary_range": "20-35K · 14薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责行芯自主EDA工具（寄生参数提取、电迁移仿真）在顶级晶圆厂PDK与客户Benchmark中的验证；
2、编写自动化回归测试脚本(Python/Shell)，分析行芯工具与国际成熟商业工具签核结果的精度偏差与Runtime；
3、深入客户芯片设计团队，提供现场技术支持与工具落地使用培训。""",
                "job_description": """【任职资格】
1、微电子或集成电路设计专业硕士及以上学历，3年以上数字或模拟后端设计/AE经验；
2、熟练掌握业界主流EDA签核流程与晶圆厂PDK规则文件语法。""",
                "source_image": "https://www.zhipin.com/gongsi/job/phy-eda.html",
                "summary": "连接自研EDA软件与晶圆代工厂前沿制程PDK，推动国产物理签核工具进入产业主流。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "EDA应用验证", "全芯片寄生参数提取黄金标准Golden校准与Benchmark比对", "must_have", 4,
                                       "熟练运用StarRC、QRC等工具进行比对测试，定位寄生电容三维场求解精度差异根因。",
                                       "精通Linux平台大规模自动化测试脚本搭建，能够快速定位软件崩溃Core Dump并复现缺陷用例。",
                                       "EDA,AE,PDK验证,寄生参数提取,Benchmark,Python", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 14. 华芯巨数（杭州）微电子有限公司 (EDA逻辑综合与形式验证)
    # -------------------------------------------------------------------------
    "华芯巨数（杭州）微电子有限公司": {
        "company_name": "华芯巨数（杭州）微电子有限公司",
        "company_intro": "前沿高科技 · 100-499人 · 芯片EDA软件 · 专注于数字芯片超大规模逻辑综合、形式验证与形式化签核EDA工具研发",
        "location_default": "杭州 · 滨江区 · 江南大道",
        "positions": [
            {
                "position_title": "EDA逻辑综合与优化核心算法研发工程师",
                "category": "EDA软件/核心算法",
                "salary_range": "32-60K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责数字集成电路高层次综合与门级逻辑优化核心算法研发（布尔匹配、面积与时序权衡优化）；
2、实现基于AIG (And-Inverter Graph) 紧凑图结构的高效逻辑重写、常数折叠及冗余消除；
3、设计针对先进制程标准单元库的高精度工艺映射(Technology Mapping)求解算法。""",
                "job_description": """【任职资格】
1、计算机科学、应用数学或微电子专业硕士及以上学历，精通离散数学与布尔逻辑运算；
2、精通现代C++，具备阅读并改进经典开源综合工具（如ABC）核心算法代码的深厚功底。""",
                "source_image": "https://www.zhipin.com/gongsi/job/huaxin-eda.html",
                "summary": "研发国产自主数字芯片逻辑综合工具，攻克百万门级电路高效布尔图优化与工艺映射。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "逻辑综合算法", "基于AIG的布尔逻辑重写与标准单元库时序映射", "must_have", 5,
                                       "精通SAT求解器在布尔等价性与逻辑覆盖中的应用，能够显著缩减门电路面积与延时乘积。",
                                       "精通多线程并行图优化算法设计，保障在超大规模数字模块综合中保持高稳定性与线性能耗。",
                                       "EDA,逻辑综合,AIG,C++,布尔优化,工艺映射", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 15. 杭州晶华微电子股份有限公司 (高精度ADC/仪器仪表芯片上市龙头)
    # -------------------------------------------------------------------------
    "杭州晶华微电子股份有限公司": {
        "company_name": "杭州晶华微电子股份有限公司",
        "company_intro": "已上市 · 100-499人 · 芯片设计/模拟IC · 科创板上市的高性能高精度模拟信号链与专用SoC芯片设计龙头",
        "location_default": "杭州 · 滨江区 · 滨安路",
        "positions": [
            {
                "position_title": "工业控制与高精度红外测温SoC设计工程师",
                "category": "芯片设计/数模混合",
                "salary_range": "25-45K · 14薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责集成24位低噪声Delta-Sigma ADC、高精度带隙基准及低功耗MCU的专用SoC架构设计；
2、负责高输入阻抗可编程增益放大器(PGA)与数字抽取滤波器(Decimation Filter)电路设计；
3、主导芯片在工业智能变送器与高精度医疗红外测温仪中的系统精度验证。""",
                "job_description": """【任职资格】
1、微电子或集成电路工程专业硕士及以上学历，3年以上高精度信号链芯片正向设计经验；
2、精通极低频微弱小信号处理，深入理解放大器输入失调与增益非线性校准机制。""",
                "source_image": "https://www.zhipin.com/gongsi/job/sdic.html",
                "summary": "设计集成24位高精度ADC与自研MCU的单芯片智能仪器仪表测量专用SoC。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "高精度信号链", "24位Sigma-Delta ADC抽取滤波与纳伏级输入噪声调优", "must_have", 5,
                                       "精通Sinc3/Sinc4数字抽取滤波器与梳状滤波器架构设计，兼顾工频50Hz/60Hz陷波抑制。",
                                       "熟练设计自校准电荷平衡积分器与低温漂带隙基准(温漂<5ppm/°C)。",
                                       "高精度ADC,SoC,红外测温,信号链,低噪声,模拟设计", 1)
                ]
            }
        ]
    }
}

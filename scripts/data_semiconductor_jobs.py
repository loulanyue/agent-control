#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
杭州全部半导体与芯片重点企业全序列真实在招岗位与能力画像权威配置库
包含 30+ 家企业的研发、制造、测试、EDA、设备、应用等完整序列职位
"""

from typing import Dict, List, Any

# 统一通用能力标签生成工具
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

SEMI_COMPANIES_FULL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # 1. 杰华特微电子股份有限公司 (已上市 · 模拟芯片龙头)
    # -------------------------------------------------------------------------
    "杰华特微电子股份有限公司": {
        "company_name": "杰华特微电子股份有限公司",
        "company_intro": "已上市 · 1000-9999人 · 芯片设计/集成电路 · 高性能模拟与数模混合芯片研发上市龙头",
        "location_default": "杭州 · 西湖区 · 浙大森林",
        "positions": [
            {
                "position_title": "高压栅极驱动芯片研发工程师 (Gate Driver IC)",
                "category": "芯片设计/模拟IC",
                "salary_range": "32-55K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 西湖区 · 浙大森林",
                "job_responsibilities": """1、负责半桥/全桥高压隔离栅极驱动芯片（Gate Driver）模拟电路设计与规格定义；
2、负责高压电平位移(Level Shift)、死区时间控制、欠压锁定(UVLO)及去饱和保护(DESAT)模块设计；
3、指导版图工程师完成高压大耐压间距与抗dv/dt共模瞬变干扰Layout设计。""",
                "job_description": """【任职资格】
1、微电子或电气工程相关专业硕士及以上学历，3年以上高压栅极驱动或隔离芯片设计经验；
2、熟悉BCD高压工艺与功率MOSFET/IGBT/SiC驱动特性，具备较强的抗干扰仿真与电路优化能力。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杰华特微电子股份有限公司",
                "summary": "负责杰华特车规与新能源高压隔离驱动芯片电路设计与关键性能仿真。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "高压驱动设计", "高压浮动栅极电平位移与抗dv/dt共模抑制", "must_have", 5,
                                       "精通高压半桥驱动拓扑，能够解决大dv/dt瞬态干扰导致的逻辑误翻转。",
                                       "熟练掌握Spectre高压仿真，针对高频开关节点进行寄生电容补偿与共模噪声抑制设计。",
                                       "Gate Driver,Level Shift,dv/dt抗扰,BCD工艺,SiC驱动", 1)
                ]
            },
            {
                "position_title": "现场应用工程师 (FAE - 储能与汽车智能座舱电源)",
                "category": "技术支持/FAE",
                "salary_range": "20-38K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 西湖区 · 浙大森林",
                "job_responsibilities": """1、负责储能、光伏逆变器及新能源汽车客户的技术方案选型推介与Design-in推进；
2、协助客户解决板级电源啸叫、EMI电磁兼容不过、温升过高及启动异常等硬件故障；
3、提炼客户端系统级电源管理需求，反馈芯片研发团队进行新产品迭代定义。""",
                "job_description": """【任职资格】
1、电力电子、电气自动化或电子信息类专业本科及以上学历，3年以上电源研发或FAE经验；
2、熟悉DCDC拓扑、BMS方案，具备独立查板调试与EMI整改攻坚能力。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杰华特微电子股份有限公司",
                "summary": "负责杰华特电源管理芯片在汽车与光储客户现场的技术攻坚与方案导入。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "板级调试与EMI整改", "车载及工业开关电源板级调试与EMI排查", "must_have", 5,
                                       "能够熟练运用示波器、电子负载与近场探头排查环路震荡与开关高频辐射尖峰。",
                                       "深入理解开关电源环路补偿及PCB电磁兼容布局法则，提供切实有效的元器件选型与滤波方案。",
                                       "FAE,EMI整改,DCDC,环路补偿,汽车电子", 1)
                ]
            },
            {
                "position_title": "ATE测试开发工程师 (Chroma/AccoTest 模拟混合信号测试)",
                "category": "芯片测试/ATE",
                "salary_range": "18-35K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 西湖区 · 浙大森林",
                "job_responsibilities": """1、负责电源管理模拟芯片CP晶圆测试与FT成品测试程序的开发与调试；
2、设计测试接口板(Load Board)与探针卡(Probe Card)，优化多工位并行测试通道利用率；
3、解决量产测试中的良率抖动、接触电阻(OS)不良，协同代工厂提升测试UPH。""",
                "job_description": """【任职资格】
1、电子科学、测控技术或微电子相关专业本科及以上学历，3年以上模拟芯片ATE开发经验；
2、熟练掌握Chroma 3380 / AccoTest STS8200机台，精通C/C++测试程序编写。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杰华特微电子股份有限公司",
                "summary": "负责模拟混合信号芯片全自动ATE测试程序开发与量产良率控制。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "ATE程序开发", "AccoTest/Chroma模拟测试方案开发与多Site并行优化", "must_have", 5,
                                       "独立完成高精度基准电压、静态功耗、过流阈值与开关频率等电参数测试方案编制。",
                                       "精通C++测试代码优化与测试板高频继电器矩阵设计，显著缩短芯片测试机时(Test Time)。",
                                       "ATE测试,AccoTest,Chroma,Loadboard,CP测试,FT测试", 1)
                ]
            },
            {
                "position_title": "芯片产品工程师 (PE - 晶圆良率与WAT异常分析)",
                "category": "产品工程/良率管控",
                "salary_range": "18-32K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 西湖区 · 浙大森林",
                "job_responsibilities": """1、负责芯片从工程样品(ES)到商业量产(MP)全生命周期良率追踪与持续改善；
2、分析晶圆代工厂WAT参数(Vth, Rdson, BV)与芯片CP测试良率的相关性；
3、主导异常批次处理(Discrepancy Lot Disposition)并推动DOE试验定位缺陷根因。""",
                "job_description": """【任职资格】
1、微电子或材料物理相关专业本科及以上学历，3年以上Fabless芯片产品工程经验；
2、精通JMP/Minitab统计分析工具，熟悉半导体高压工艺制造机理。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杰华特微电子股份有限公司",
                "summary": "负责晶圆制造代工厂工艺参数追踪与批量量产良率综合改善。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "良率分析", "WAT数据统计分析与CP低良率根因定位", "must_have", 4,
                                       "具备将晶圆测试电学参数与物理缺陷图谱(Wafer Map)进行多变量相关性分析能力。",
                                       "熟练运用JMP进行SPC统计制程控制与正态分布检验，及时拦截晶圆厂工艺漂移风险。",
                                       "PE,良率改善,WAT,Wafer Map,JMP,SPC", 1)
                ]
            },
            {
                "position_title": "数字电源算法与控制芯片工程师 (数字环路拓扑)",
                "category": "芯片设计/控制算法",
                "salary_range": "30-52K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 西湖区 · 浙大森林",
                "job_responsibilities": """1、负责数字电源芯片控制环路算法离散化建模、Z域系统仿真与定点数实现；
2、设计LLC、移相全桥及交错PFC拓扑的自适应死区、变频与变占空比控制策略；
3、协同数字前端工程师完成算法逻辑的RTL代码转化与硬件协同仿真。""",
                "job_description": """【任职资格】
1、控制理论、电气工程或微电子专业硕士及以上学历，熟悉MATLAB/Simulink离散建模；
2、深入理解开关电源非线性控制、数字PID/双闭环控制理论。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杰华特微电子股份有限公司",
                "summary": "负责新一代数字电源控制芯片离散控制算法架构与建模验证。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "控制算法", "数字电源Z域离散建模与闭环控制算法设计", "must_have", 5,
                                       "掌握双线性变换与离散PID、自适应控制算法推导，完成大动态瞬态稳定性校核。",
                                       "熟练使用Simulink进行定点化量化误差与极限环振荡分析，指导数字硬件架构设计。",
                                       "数字电源,Simulink,离散建模,LLC控制,Z域变换", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 2. 杭州富芯半导体有限公司 (12英寸模拟晶圆制造龙头)
    # -------------------------------------------------------------------------
    "杭州富芯半导体有限公司": {
        "company_name": "杭州富芯半导体有限公司",
        "company_intro": "国企/大型民营合资 · 1000-9999人 · 半导体晶圆制造 · 浙江省首条12英寸特色工艺模拟集成电路晶圆制造生产线",
        "location_default": "杭州 · 钱塘区 · 大江东产业集聚区",
        "positions": [
            {
                "position_title": "刻蚀工艺研发主任工程师 (Dry Etch / Lam Research机台)",
                "category": "晶圆制造/刻蚀工艺",
                "salary_range": "28-45K · 15薪",
                "experience_req": "5-10年",
                "education_req": "本科及以上",
                "location": "杭州 · 钱塘区 · 大江东",
                "job_responsibilities": """1、主导12英寸晶圆深硅刻蚀、栅极介质刻蚀及金属间介质刻蚀工艺配方(Recipe)研发；
2、攻坚刻蚀线宽(CD)均匀性、侧壁倾角及微负载效应(Micro-loading Effect)关键质量难点；
3、负责Lam Research / AMAT等离子体刻蚀设备工艺选型评估与腔体状态稳定性监控。""",
                "job_description": """【任职资格】
1、微电子、化学工程、材料科学相关专业本科及以上学历，5年以上12英寸先进晶圆厂刻蚀工艺经验；
2、精通等离子体刻蚀物理机理与高深宽比刻蚀工艺调优。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州富芯半导体有限公司",
                "summary": "负责12英寸特色工艺线等离子干法刻蚀核心技术配方开发与工艺窗口拓宽。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "刻蚀工艺", "高深宽比等离子体刻蚀CD均匀性与选择比控制", "must_have", 5,
                                       "熟练调优气体流量、射频功率偏压与腔室压强配比，实现高垂直度无侧蚀轮廓控制。",
                                       "精通常见刻蚀副产物沉积抑制与腔体干法清洗(Dry Clean)工艺参数设定。",
                                       "刻蚀,Dry Etch,Lam Research,CD均匀性,等离子体", 1)
                ]
            },
            {
                "position_title": "薄膜沉积工艺工程师 (PVD/CVD / 溅射工艺)",
                "category": "晶圆制造/薄膜工艺",
                "salary_range": "20-35K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 钱塘区 · 大江东",
                "job_responsibilities": """1、负责12英寸晶圆金属互连PVD薄膜（Cu/Ti/TiN）及介质CVD薄膜（SiO2/SiN）沉积工艺；
2、优化薄膜厚度均匀性、应力(Stress)、粗糙度及颗粒污染(Defect/Particle)；
3、主导新材料薄膜台阶覆盖率(Step Coverage)改善试验，提升晶圆金属化层可靠性。""",
                "job_description": """【任职资格】
1、材料物理、应用化学或微电子专业本科及以上学历，3年以上晶圆制造厂薄膜工艺实操经验；
2、熟悉AMAT Endura/Centura或TEL薄膜设备操作与维护规范。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州富芯半导体有限公司",
                "summary": "负责12英寸半导体薄膜沉积设备工艺配方调整与纳米级台阶覆盖率优化。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "薄膜沉积", "PVD金属化与CVD高台阶覆盖率薄膜生长", "must_have", 4,
                                       "掌握深孔介质填充与阻挡层沉积工艺物理原理，实现极低界面接触电阻与零空洞。",
                                       "具备精确调控射频磁控溅射靶材剥离与薄膜内应力的工程经验。",
                                       "PVD,CVD,薄膜应力,台阶覆盖率,AMAT", 1)
                ]
            },
            {
                "position_title": "CMP化学机械抛光工艺工程师 (Copper/Oxide CMP)",
                "category": "晶圆制造/CMP工艺",
                "salary_range": "22-36K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 钱塘区 · 大江东",
                "job_responsibilities": """1、负责12英寸铜大马士革(Cu Damascene)工艺及层间介质氧化物CMP平坦化工艺开发；
2、监控和解决CMP抛光后晶圆表面划伤(Scratch)、碟形凹陷(Dishing)及侵蚀(Erosion)；
3、评测新型抛光液(Slurry)、抛光垫(Pad)及修整盘(Conditioner)在量产中的表现。""",
                "job_description": """【任职资格】
1、化学、材料或微电子工程专业本科及以上学历，3年以上晶圆厂CMP工艺开发经验；
2、熟悉Ebara或AMAT Reflexion CMP抛光机台原理。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州富芯半导体有限公司",
                "summary": "负责12英寸晶圆全局超精密平坦化CMP工艺开发与表面微米级缺陷控制。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "CMP平坦化", "大马士革铜CMP表面微划伤与碟形下陷控制", "must_have", 4,
                                       "精通抛光压力、研磨头分区加压曲线与研磨液配比，实现全局平坦化高选择比。",
                                       "具备通过后清洗化学液配比有效消除抛光残留微粒颗粒的工艺解决能力。",
                                       "CMP,平坦化,Dishing,Slurry,Ebara,研磨", 1)
                ]
            },
            {
                "position_title": "半导体厂务系统工程师 (超纯水UPW/高纯特气系统)",
                "category": "厂务设施/动力保障",
                "salary_range": "18-30K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 钱塘区 · 大江东",
                "job_responsibilities": """1、负责12英寸晶圆厂超纯水(UPW)处理系统、高纯特气(SiH4/NF3等)输送管网的24小时不间断安全运行；
2、实时监控超纯水电阻率(18.2 MΩ·cm)、TOC有机碳及特气纯度ppb级指标；
3、主导厂务系统预防性维护计划与危险化学品泄漏应急响应预案执行。""",
                "job_description": """【任职资格】
1、给排水、化学工程、环境工程或暖通动力专业本科及以上学历，3年以上半导体洁净厂务运行经验；
2、熟悉半导体特种气体输送系统(Gas Jungle)与双套管安全联锁防护机制。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州富芯半导体有限公司",
                "summary": "保障12英寸晶圆制造生命线——超纯水与易燃有毒高纯特气供应系统极致稳定。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "厂务特气水处理", "18.2M超纯水净化与高纯特种气体安全调度", "must_have", 4,
                                       "熟悉反渗透RO、电去离子EDI与紫外杀菌闭环工艺，保证ppb级水质达标。",
                                       "精通特气气柜(Gas Cabinet)自动吹扫切换逻辑与剧毒可燃气体泄漏报警联动处置。",
                                       "厂务,超纯水,UPW,特气系统,洁净室,EHS", 1)
                ]
            },
            {
                "position_title": "CIM/MES智能制造系统研发工程师 (半导体晶圆制造)",
                "category": "软件工程/CIM系统",
                "salary_range": "25-42K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 钱塘区 · 大江东",
                "job_responsibilities": """1、负责晶圆制造核心MES(制造执行系统)与EAP(设备自动化联机)系统的开发与功能迭代；
2、实现晶圆批次(Lot)在光刻、刻蚀、薄膜等全工序机台的自动派工(Dispatching)与Recipe自动下载；
3、设计晶圆制造实时报警(SPC)与良率溯源系统，保障7x24小时高并发零中断运行。""",
                "job_description": """【任职资格】
1、计算机科学、软件工程相关专业本科及以上学历，3年以上晶圆制造Fab厂CIM/MES开发经验；
2、熟悉SECS/GEM通信协议标准，精通Java/C#及Oracle数据库高可用架构。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州富芯半导体有限公司",
                "summary": "构筑12英寸智能晶圆制造工厂神经中枢，驱动全自动派工与机台数据物联。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "CIM智能制造", "SECS/GEM机台联机与晶圆MES自动化派工流设计", "must_have", 5,
                                       "精通SEMI标准通讯规范（E4/E5/E30/E37），具备EAP与底层晶圆机台稳定对接能力。",
                                       "熟练设计晶圆WIP在制品流转、返工Route分支及载具(FOUP)物流搬送自动化控制逻辑。",
                                       "MES,CIM,SECS/GEM,EAP,晶圆制造,自动化派工", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 3. 平头哥（杭州）半导体有限公司 (阿里旗下全栈芯片设计旗舰)
    # -------------------------------------------------------------------------
    "平头哥（杭州）半导体有限公司": {
        "company_name": "平头哥（杭州）半导体有限公司",
        "company_intro": "头部互联网芯片大厂 · 1000-9999人 · 芯片设计/处理器 · 阿里巴巴旗下半导体芯片核心研发实体",
        "location_default": "杭州 · 余杭区 · 未来科技城",
        "positions": [
            {
                "position_title": "SoC系统互联与总线架构设计专家 (NoC / AXI / CHI)",
                "category": "芯片设计/数字IC",
                "salary_range": "35-65K · 16薪",
                "experience_req": "5-10年",
                "education_req": "硕士及以上",
                "location": "杭州 · 余杭区 · 未来科技城",
                "job_responsibilities": """1、负责多核高性能服务器及端侧AI芯片片上互联网络(NoC / Crossbar)架构设计与建模；
2、负责ARM AMBA AXI5 / CHI一致性总线协议实现，优化片上多级缓存与内存子系统带宽；
3、主导系统端到端时延、服务质量(QoS)分配与死锁/饥饿避免(Deadlock Prevention)仿真验证。""",
                "job_description": """【任职资格】
1、计算机体系结构、微电子专业硕士及以上学历，5年以上高性能SoC芯片互联架构设计经验；
2、深入理解片上缓存一致性协议(Cache Coherency)与片上网络路由器拓扑设计。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=平头哥（杭州）半导体有限公司",
                "summary": "负责超大规模多核处理器片上高速总线互联与高并发缓存一致性架构实现。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "片上互联架构", "AMBA CHI缓存一致性协议与高吞吐NoC架构设计", "must_have", 5,
                                       "深刻掌握MESI/MOESI状态机转移，能够在复杂乱序访问场景下保证数据严格一致性。",
                                       "熟练构建SystemC/Python体系结构性能模型，针对存储瓶颈完成QoS带宽调度优化。",
                                       "SoC互联,NoC,AMBA CHI,AXI5,缓存一致性,架构设计", 1)
                ]
            },
            {
                "position_title": "神经网络加速器(NPU)微架构研发工程师",
                "category": "芯片设计/AI芯片",
                "salary_range": "35-60K · 16薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 余杭区 · 未来科技城",
                "job_responsibilities": """1、负责端云结合大模型推理加速专用NPU计算引擎微架构设计与RTL开发；
2、设计高能效矩阵乘法脉动阵列(Systolic Array)、稀疏化计算单元及片上SRAM数据复用流水线；
3、协同深度学习编译器团队完成算子映射(Operator Mapping)与指令集(ISA)微架构定义。""",
                "job_description": """【任职资格】
1、微电子、计算机专业硕士及以上学历，3年以上专用AI加速器或GPU微架构设计经验；
2、熟悉Transformer、CNN等主流深度学习模型计算特征与定点化量化算法。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=平头哥（杭州）半导体有限公司",
                "summary": "研发平头哥自主AI芯片专用计算核心，突破端侧大模型超低功耗推理算力瓶颈。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "NPU计算架构", "脉动阵列与大模型算子硬件加速微架构实现", "must_have", 5,
                                       "精通基于硬件数据流(Dataflow)的Weight Stationary / Output Stationary缓存复用设计。",
                                       "具备将高维矩阵张量运算高效拆解并映射至专用硬件向量执行部件的能力。",
                                       "NPU,脉动阵列,AI芯片,微架构,Transformer加速,Verilog", 1)
                ]
            },
            {
                "position_title": "芯片物理设计后端实现工程师 (APR / Innovus / 时序签核)",
                "category": "芯片设计/后端实现",
                "salary_range": "28-50K · 15薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 余杭区 · 未来科技城",
                "job_responsibilities": """1、负责先进纳米制程（FinFET/GAA）超大规模复杂SoC芯片物理布局布线(P&R)；
2、主导时钟树综合(CTS)、拥塞消除(Congestion Optimization)及多电源域低功耗UPF实现；
3、执行静态时序分析(STA)、信号完整性分析(SI)与物理规则检查(DRC/LVS/Antenna)签核。""",
                "job_description": """【任职资格】
1、微电子或通信工程相关专业本科及以上学历，3年以上先进制程芯片后端实现经验；
2、精通Cadence Innovus或Synopsys ICC2，熟练编写Tcl/Perl自动化脚本。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=平头哥（杭州）半导体有限公司",
                "summary": "攻克先进制程千兆门级超大规模芯片时钟树综合与物理时序闭环签核挑战。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "芯片后端实现", "先进制程CTS时钟树构建与STA时序收敛", "must_have", 5,
                                       "精通常见时序违例(Setup/Hold/Skew)在极端工艺角(PVT Corner)下的修收敛策略。",
                                       "熟练应对多电压多电源域(UPF)布局隔离与电迁移(EM)、电源压降(IR-Drop)联合分析。",
                                       "APR,Innovus,STA,CTS,FinFET,物理设计", 1)
                ]
            },
            {
                "position_title": "高速SerDes数模混合IP研发工程师 (PCIe 5.0 / DDR5 PHY)",
                "category": "芯片设计/数模混合",
                "salary_range": "35-65K · 16薪",
                "experience_req": "5-8年",
                "education_req": "硕士及以上",
                "location": "杭州 · 余杭区 · 未来科技城",
                "job_responsibilities": """1、负责32Gbps+ 超高速SerDes物理层(PHY)电路架构设计与仿真验证；
2、设计CTLE连续时间线性均衡器、DFE判决反馈均衡器、高频低抖动PLL及CDR时钟恢复模块；
3、主导芯片流片后高速眼图测试、抖动分解(Jitter Decomposition)与误码率(BER)调测。""",
                "job_description": """【任职资格】
1、微电子或集成电路专业硕士及以上学历，5年以上高速SerDes或DDR PHY研发实操经验；
2、深入理解信道高频损耗衰减机理与数模混合自适应校准算法。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=平头哥（杭州）半导体有限公司",
                "summary": "研发支撑数据中心与云端算力互联的32G/56G超高速SerDes核心数模IP。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "高速SerDes设计", "高频低抖动PLL与自适应均衡器(CTLE/DFE)电路设计", "must_have", 5,
                                       "熟练掌握PAM4/NRZ调制下的高频电路仿真，能够针对信道损耗设计闭环校准算法。",
                                       "具备熟练使用高带宽示波器与误码仪分析眼图抖动分布及阻抗匹配的硬件实测技能。",
                                       "SerDes,PCIe,DDR PHY,CTLE,DFE,PLL,高速接口", 1)
                ]
            },
            {
                "position_title": "RISC-V底层编译工具链与内核优化工程师 (LLVM/GCC/Linux)",
                "category": "底层软件/系统开发",
                "salary_range": "28-50K · 16薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 余杭区 · 未来科技城",
                "job_responsibilities": """1、负责平头哥玄铁RISC-V处理器专用指令集扩展在LLVM/GCC编译器的后端优化；
2、主导Linux内核在RISC-V架构上的移植适配、MMU虚拟内存管理及中断子系统性能调优；
3、分析和优化典型计算负载在自研CPU核上的执行微架构瓶颈(IPC/Cache Miss)。""",
                "job_description": """【任职资格】
1、计算机科学或软件工程本科及以上学历，3年以上编译器后端或操作系统底层开发经验；
2、深入理解RISC-V特权级体系结构与编译原理指令调度算法。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=平头哥（杭州）半导体有限公司",
                "summary": "打通玄铁RISC-V芯片到底层操作系统与编译器的软硬件全栈性能通途。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "底层系统软件", "LLVM编译后端代码生成与Linux内核RISC-V适配", "must_have", 5,
                                       "熟练编写LLVM TableGen描述文件并优化循环展开、指令调度与寄存器分配。",
                                       "深入掌握Linux内核汇编级启动流程、SMP多核调度与设备树(Device Tree)驱动框架。",
                                       "RISC-V,LLVM,GCC,Linux内核,编译优化,玄铁", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 4. 杭州士兰微电子股份有限公司 (上市IDM半导体龙头)
    # -------------------------------------------------------------------------
    "杭州士兰微电子股份有限公司": {
        "company_name": "杭州士兰微电子股份有限公司",
        "company_intro": "已上市 · 5000-9999人 · 半导体制造/IDM · 国内综合实力顶尖的芯片设计与晶圆制造一体化IDM龙头",
        "location_default": "杭州 · 钱塘区 / 滨江区",
        "positions": [
            {
                "position_title": "车规级功率模块(IGBT Module)结构设计工程师",
                "category": "封测工程/功率模块",
                "salary_range": "25-45K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 钱塘区",
                "job_responsibilities": """1、负责新能源汽车主电机驱动高压大电流IGBT/SiC功率模块的拓扑与物理结构设计；
2、主导DBC/AMB陶瓷基板布局、铜排汇流条设计及超声波铝线/铜线键合工艺参数匹配；
3、运用ANSYS开展模块热-机-电耦合仿真，优化散热水冷底板热阻与寄生杂散电感(Ls)。""",
                "job_description": """【任职资格】
1、机械工程、微电子或材料物理相关专业本科及以上学历，3年以上汽车功率模块研发经验；
2、熟练掌握功率模块高可靠封装材料（环氧塑封料、纳米银烧结、无铅焊料）特性。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州士兰微电子股份有限公司",
                "summary": "攻克新能源汽车主驱核心800V碳化硅/IGBT大功率模块散热与极低寄生电感设计。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "功率模块封装", "车规IGBT/SiC模块散热仿真与低杂散电感铜排设计", "must_have", 5,
                                       "精通Q3D寄生参数提取与Icepak热仿真，将模块主回路寄生电感压降至10nH以下。",
                                       "熟悉汽车级AQG324功率模块测试标准，具备解决功率循环与温度循环分层失效的能力。",
                                       "IGBT模块,SiC,车规封装,寄生电感,ANSYS仿真,AQG324", 1)
                ]
            },
            {
                "position_title": "现场应用工程师 (FAE - 白电变频与工业电机)",
                "category": "技术支持/FAE",
                "salary_range": "18-35K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责变频空调、变频洗衣机及工业伺服驱动客户的IPM智能功率模块技术推广；
2、协助客户解决电机三相逆变器相电流采样漂移、过流自举电路异常及温升超标问题；
3、配合客户进行电机FOC矢量控制算法在士兰微MCU及驱动芯片上的落地调优。""",
                "job_description": """【任职资格】
1、电气工程、电力电子相关专业本科及以上学历，3年以上电机控制或变频电源FAE经验；
2、精通永磁同步电机(PMSM) FOC控制算法，具备扎实的硬件示波器实测调试功底。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州士兰微电子股份有限公司",
                "summary": "推动士兰微自主IPM功率模块与变频MCU在白电及工业自动化客户的大规模商用。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "电机驱动调测", "电机FOC算法调试与IPM模块外围自举驱动优化", "must_have", 4,
                                       "熟练运用矢量控制理论，解决电机低速重载抖动、死区谐波补偿及弱磁控制难题。",
                                       "熟练排查客户端逆变桥臂直通短路故障，保障高压功率管安全工作区(SOA)。",
                                       "FAE,电机驱动,IPM模块,FOC控制,变频器", 1)
                ]
            },
            {
                "position_title": "MEMS惯性传感器研发工程师 (加速度计/陀螺仪)",
                "category": "芯片设计/MEMS器件",
                "salary_range": "25-45K · 14薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责微机电系统(MEMS)电容式三轴加速度计与陀螺仪微机械敏感结构设计；
2、使用CoventorWare / COMSOL对微机械梳齿谐振频率、阻尼系数及机械灵敏度进行多物理场仿真；
3、协同晶圆厂优化MEMS深硅刻蚀(DRIE)高深宽比工艺与晶圆级真空键合封装。""",
                "job_description": """【任职资格】
1、仪器科学、微电子、精密仪器专业硕士及以上学历，3年以上MEMS惯性器件正向研发经验；
2、熟悉MEMS前道加工工艺与专用接口读出ASIC电路协同仿真。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州士兰微电子股份有限公司",
                "summary": "负责士兰微全自主IDM微机电惯性传感器微观敏感机械结构设计与多物理场仿真。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "MEMS结构仿真", "梳齿微机械敏感结构多物理场耦合仿真与工艺匹配", "must_have", 5,
                                       "精确建立MEMS器件热-电-机械耦合数学模型，优化品质因数Q值与抗震耐冲击性能。",
                                       "深入掌握硅-玻璃阳极键合与硅-硅熔融键合界面应力控制，实现长期零偏稳定性。",
                                       "MEMS,加速度计,陀螺仪,COMSOL,DRIE,微结构", 1)
                ]
            },
            {
                "position_title": "半导体器件失效分析专家 (功率器件高压雪崩破坏机理)",
                "category": "质量与可靠性/FA",
                "salary_range": "20-38K · 14薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 钱塘区",
                "job_responsibilities": """1、主导高压MOSFET、IGBT在单脉冲雪崩(UIS)及短路(SCSOA)工况下烧毁失效样片的深度物理分析；
2、运用微光显微镜(PHEMOS)、激光热点定位(OBIRCH)及聚焦离子束(FIB)切片准确定位晶圆内部微小缺陷；
3、编写专业分析报告，指引器件物理结构与终端保护环(Guard Ring)工艺改进。""",
                "job_description": """【任职资格】
1、半导体物理、微电子学相关专业硕士及以上学历，3年以上高压功率器件失效分析经验；
2、深入理解功率半导体寄生晶体管闩锁(Latch-up)与局部电流丝集聚机理。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州士兰微电子股份有限公司",
                "summary": "深入微观晶圆物理缺陷，破解高压大功率器件雪崩耐量与热击穿机理瓶颈。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "功率器件FA", "UIS雪崩热击穿微观定位与FIB高精度切片解析", "must_have", 5,
                                       "精通利用SEM扫描电镜及EDS能谱分析晶圆金属化层互扩散与氧化层电击穿形貌。",
                                       "能够结合器件半导体物理能带理论，从根因上溯源流片工艺缺陷与应用过应力(EOS)。",
                                       "失效分析,FA,UIS雪崩,FIB,OBIRCH,功率半导体", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 5. 浙江力积存储科技股份有限公司 (存储芯片设计与测试龙头)
    # -------------------------------------------------------------------------
    "浙江力积存储科技股份有限公司": {
        "company_name": "浙江力积存储科技股份有限公司",
        "company_intro": "拟上市/高新企业 · 100-499人 · 芯片设计/存储器 · 专注于DRAM、SRAM与闪存控制器自主研发的核心存储芯片领军企业",
        "location_default": "杭州 · 滨江区 · 科技馆街",
        "positions": [
            {
                "position_title": "高速低功耗DRAM芯片模拟电路研发工程师",
                "category": "芯片设计/存储IC",
                "salary_range": "30-55K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责LPDDR4/4X及DDR3高速动态随机存取存储器模拟模块（内部偏置泵压泵、感知放大器Sense Amp、定时控制）电路设计；
2、负责DRAM阵列超低功耗待机漏电流抑制与自刷新(Self-Refresh)电路优化；
3、指导版图团队完成亚微米紧凑型存储单元矩阵的高对称、极低寄生电容Layout布局。""",
                "job_description": """【任职资格】
1、集成电路、微电子专业硕士及以上学历，3年以上DRAM或SRAM正向存储芯片研发经验；
2、熟练掌握HSPICE/Spectre仿真工具，深入理解电荷共享原理与灵敏度放大器读写时序裕量。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=浙江力积存储科技股份有限公司",
                "summary": "研发自研低功耗DRAM芯片模拟外围电路与高灵敏度差分读出放大器架构。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "DRAM模拟设计", "存储阵列读出放大器(Sense Amp)与内部升压泵设计", "must_have", 5,
                                       "精通微伏级微弱电荷快速鉴别差分放大电路设计，具备毫微微法级电容瞬态充放电精确建模能力。",
                                       "深刻掌握高低温工艺偏差下字线驱动(Wordline Driver)负压生成与自刷新时钟稳定性。",
                                       "DRAM,LPDDR,Sense Amp,存储芯片,自刷新,模拟IC", 1)
                ]
            },
            {
                "position_title": "存储器ATE测试程序开发工程师 (Advantest / Chroma平台)",
                "category": "芯片测试/ATE",
                "salary_range": "18-35K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责DRAM与闪存芯片晶圆级CP与成品FT高速功能测试向量转换与测试程序编写；
2、开发存储器复杂测试算法图案（March C-, Checkerboard, Butterfly），全覆盖抓取单元缺陷；
3、设计多芯片堆叠封装测试夹具，解决千兆频宽下测试座接触阻抗与信号串扰抖动。""",
                "job_description": """【任职资格】
1、电子信息、测控技术相关专业本科及以上学历，3年以上存储芯片量产ATE测试经验；
2、精通爱德万Advantest T5386/T5503或Chroma 3650存储测试系统。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=浙江力积存储科技股份有限公司",
                "summary": "构建高覆盖率存储器物理缺陷筛选算法测试图案与多Site超高速自动化机台程序。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "存储测试算法", "March算法测试图案编写与高频眼图时序裕量校准", "must_have", 5,
                                       "掌握各类故障模型（SAF, AF, CF）对应测试Pattern的设计与优化，提高测试效率与检出率。",
                                       "熟练编写测试程序实现存储阵列激光修补(Laser Repair)与电气熔丝(eFuse)重映射算法。",
                                       "ATE,DRAM测试,March算法,Advantest,eFuse,FT测试", 1)
                ]
            },
            {
                "position_title": "存储芯片物理版图设计工程师 (高密DRAM单元阵列)",
                "category": "芯片设计/模拟版图",
                "salary_range": "18-32K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责高密度DRAM存储单元、解码器(Decoder)及数据线驱动器版图精确布局；
2、攻坚字线(Wordline)与位线(Bitline)的超高密度平行布线寄生电容耦合与串扰屏蔽；
3、执行版图DRC/LVS验证、虚设金属(Dummy Metal)填充及ESD与抗闩锁规则签核。""",
                "job_description": """【任职资格】
1、微电子或集成电路设计专业本科及以上学历，3年以上存储芯片全定制版图设计经验；
2、熟练掌握Virtuoso Layout Suite及Calibre物理验证工具。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=浙江力积存储科技股份有限公司",
                "summary": "实现存储芯片超高集成度物理微观版图绘制与纳米级位线寄生电容优化。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "存储全定制版图", "高密阵列字线位线寄生电容隔离与对称匹配版图", "must_have", 4,
                                       "深入掌握深亚微米光刻邻近效应(OPC)规则与多重曝光图形限制下的版图实现技巧。",
                                       "具备精确匹配差分感知放大器对称器件布局以消除失调电压(Offset Voltage)的实战经验。",
                                       "版图,DRAM版图,Bitline,Virtuoso,Calibre,全定制", 1)
                ]
            },
            {
                "position_title": "存储控制器数字前端设计工程师 (NAND/DRAM Controller)",
                "category": "芯片设计/数字IC",
                "salary_range": "28-50K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、负责自研存储控制芯片协议逻辑（ONFI/Toggle NAND接口、AXI总线从机接口）开发；
2、负责高吞吐硬件DMA传输引擎、磨损均衡调度及低延迟命令队列仲裁器设计；
3、配合算法团队实现硬件LDPC纠错引擎及AES硬件加密逻辑的RTL实现与仿真验证。""",
                "job_description": """【任职资格】
1、微电子、通信工程或计算机专业硕士及以上学历，3年以上存储控制器逻辑设计经验；
2、熟练掌握Verilog/SystemVerilog，深入理解NAND Flash物理层协议与总线时序。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=浙江力积存储科技股份有限公司",
                "summary": "负责存储控制器高速硬件接口逻辑、DMA通道及硬件加速仲裁器正向设计。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "存储控制器逻辑", "ONFI协议引擎与多通道DMA硬件调度器设计", "must_have", 5,
                                       "精通高速同步时序设计与跨时钟域(CDC)处理，确保多通道并发无数据冲突。",
                                       "具备基于UVM平台搭建存储控制器模块级与系统级验证环境的能力。",
                                       "存储控制器,ONFI,DMA,Verilog,SystemVerilog,数字前端", 1)
                ]
            },
            {
                "position_title": "存储芯片可靠性验证工程师 (高低温数据保持测试 / HTOL)",
                "category": "质量与可靠性/测试",
                "salary_range": "16-30K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 滨江区",
                "job_responsibilities": """1、制定存储芯片高温工作寿命试验(HTOL)、高低温偏压循环(THB)及高加速温湿度应力试验(HAST)方案；
2、搭建多通道自动化老化测试系统，长期监测极端环境下的数据保持(Retention)与耐久性(Endurance)；
3、撰写芯片JEDEC可靠性合规认证报告，协助车规与工规客户完成可靠性导入。""",
                "job_description": """【任职资格】
1、材料物理、微电子、可靠性工程专业本科及以上学历，3年以上半导体可靠性试验经验；
2、熟悉JEDEC JESD22与AEC-Q100可靠性标准，熟练操作温湿度老化试验箱与老化板。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=浙江力积存储科技股份有限公司",
                "summary": "执行严苛的JEDEC/AEC车规级存储芯片长期数据保持与高加速应力老化测试验证。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "存储可靠性", "JEDEC标准HTOL老化试验与数据保持漂移监测", "must_have", 4,
                                       "熟练运用Arrhenius模型推导激活能与加速因子，推算芯片在工作寿命期内的FIT失效率。",
                                       "具备独立搭建高密度老化测试板及自动数据采集脚本排查早期失效(Infant Mortality)的能力。",
                                       "可靠性,HTOL,JEDEC,数据保持,AEC-Q100,测试", 1)
                ]
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 6. 杭州茂力半导体技术有限公司 (MPS 杭州研发中心)
    # -------------------------------------------------------------------------
    "杭州茂力半导体技术有限公司": {
        "company_name": "杭州茂力半导体技术有限公司",
        "company_intro": "外资独资/美资上市 · 1000-9999人 · 芯片设计/半导体 · 全球顶级高性能模拟半导体与电源管理方案研发巨头MPS在杭主力研发中心",
        "location_default": "杭州 · 上城区 / 滨江区",
        "positions": [
            {
                "position_title": "大电流多相数字电源控制器设计工程师 (Multi-Phase VR14)",
                "category": "芯片设计/模拟IC",
                "salary_range": "35-65K · 16薪",
                "experience_req": "5-8年",
                "education_req": "硕士及以上",
                "location": "杭州 · 上城区",
                "job_responsibilities": """1、负责面向AI服务器GPU与CPU供电的多相(Multi-Phase)大电流数字电源芯片架构设计；
2、负责数字电流纹波均衡分配、超快瞬态响应(ACOT/COT)增强电路及PMBus遥测模块设计；
3、主导芯片在数千安培(KA)级动态大电流载荷下的系统级仿真与芯片实测。""",
                "job_description": """【任职资格】
1、微电子或电力电子专业硕士及以上学历，5年以上服务器大功率电源芯片设计经验；
2、精通Intel VR13/VR14及AMD SVI3电源规范，深入理解超高动态负载瞬态恢复机制。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州茂力半导体技术有限公司",
                "summary": "设计支撑顶级AI大模型服务器GPU核心供电的多相超大电流数字电源控制器芯片。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "多相电源控制", "Intel VR14规范多相电流均衡与自适应瞬态响应架构", "must_have", 5,
                                       "掌握微秒级负载阶跃下多相交错动态均流算法，抑制输出电压过冲与欠冲。",
                                       "精通数模混合仿真与非线性环路补偿设计，保障多相并联拓扑的绝对应急稳定性。",
                                       "Multi-Phase,VR14,AI服务器供电,ACOT,模拟IC,PMBus", 1)
                ]
            },
            {
                "position_title": "芯片应用评估工程师 (AE - 服务器与GPU供电模组)",
                "category": "系统工程/AE",
                "salary_range": "25-45K · 15薪",
                "experience_req": "3-5年",
                "education_req": "硕士及以上",
                "location": "杭州 · 上城区",
                "job_responsibilities": """1、负责MPS新一代集成DrMOS功率级与多相控制器评估板(EVB)硬件设计与极端工况调试；
2、测量电源模块效率曲线、相位裕度、开关死区时间、输入反射波形与电热分布；
3、编写权威芯片技术参考手册(Datasheet/App Note)，为头部云厂商数据中心定制供电方案。""",
                "job_description": """【任职资格】
1、电力电子或电气工程专业硕士及以上学历，3年以上高频高密度开关电源研发经验；
2、熟练操作矢量网络分析仪(Bode 100)、高频罗氏线圈及热成像仪。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州茂力半导体技术有限公司",
                "summary": "针对服务器与算力中心超级供电模组进行系统级性能极限评估与参考方案开发。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "系统评估调试", "高频大功率DrMOS板级调试与环路稳定性Bode图测量", "must_have", 5,
                                       "精通利用Bode 100测量开关电源闭环相位裕度与增益裕度，提供精确的补偿网络参数。",
                                       "熟练进行PCB热仿真与大电流走线寄生电感仿真，优化多层板高频去耦电容布局。",
                                       "AE,DrMOS,Bode图,环路测试,服务器电源,高功率密度", 1)
                ]
            },
            {
                "position_title": "现场应用工程师 (FAE - 汽车智能座舱与高阶辅助驾驶电源)",
                "category": "技术支持/FAE",
                "salary_range": "22-40K · 15薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 上城区",
                "job_responsibilities": """1、负责主流汽车主机厂与Tier-1智能座舱域控制器及自动驾驶SOC芯片供电技术支持；
2、解决车规冷启动(Cold Crank)、抛负载(Load Dump)及CISPR-25 Class 5车规EMI电磁干扰；
3、推动MPS车规级电源芯片在整车厂的Design-Win与量产保供。""",
                "job_description": """【任职资格】
1、汽车电子、自动化或电子工程专业本科及以上学历，3年以上汽车半导体FAE经验；
2、深入理解车规AEC-Q100标准与ISO 7637-2汽车电气瞬变抗扰测试。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州茂力半导体技术有限公司",
                "summary": "攻关智能网联汽车域控制器核心电源供电架构，突破车规级严苛电磁兼容与抛负载防护。",
                "status": "active",
                "requirements": [
                    create_requirement("工程与技术", "汽车电子FAE", "CISPR 25 Class 5车规EMI整改与Load Dump防护", "must_have", 5,
                                       "掌握展频调制(Spread Spectrum)与低EMI封装技术的应用技巧，解决中短波辐射超标难题。",
                                       "能够独立根据整车厂电气工况设计TVS瞬态浪涌吸收网络与反极性保护电路。",
                                       "FAE,汽车电子,智能座舱,CISPR-25,Load Dump,EMI整改", 1)
                ]
            },
            {
                "position_title": "模拟IC测试开发工程师 (ETS-364 / Eagle 模拟混合机台)",
                "category": "芯片测试/ATE",
                "salary_range": "20-36K · 14薪",
                "experience_req": "3-5年",
                "education_req": "本科及以上",
                "location": "杭州 · 上城区",
                "job_responsibilities": """1、负责高压大电流DC-DC、电机驱动芯片在Eagle ETS-364 / ETS-88机台的CP/FT测试方案设计；
2、设计高频大电流探针卡与测试底板，优化大电流Kelvin开尔文四线传感开路检测；
3、协同晶圆厂与封装厂推进测试时间压缩(Test Time Reduction)与测试良率稳定性追踪。""",
                "job_description": """【任职资格】
1、微电子、测控或仪器类专业本科及以上学历，3年以上Teradyne Eagle机台实操经验；
2、精通C/C++测试程序开发，熟悉高精度电源与多通道电压电流源配置。""",
                "source_image": "https://www.zhipin.com/web/geek/jobs?city=101210100&query=杭州茂力半导体技术有限公司",
                "summary": "负责MPS全球顶尖模拟电源芯片在ETS-364机台的高精度量产测试程序研发。",
                "status": "active",
                "requirements": [
                    create_requirement("专业能力", "Eagle ATE测试", "ETS-364大电流Kelvin测试接口开发与多Site测试优化", "must_have", 4,
                                       "精通大电流脉冲测试下的接触阻抗压降补偿与感性反峰电压吸收防护电路设计。",
                                       "熟练编写测试程序实现毫安级与微安级微弱静态功耗的高速精准多通道测量。",
                                       "ATE测试,Eagle,ETS-364,Kelvin测试,量产测试,模拟芯片", 1)
                ]
            }
        ]
    }
}

try:
    from scripts.data_semiconductor_jobs_part2 import SEMI_COMPANIES_PART2_REGISTRY
    from scripts.data_semiconductor_jobs_part3 import SEMI_COMPANIES_PART3_REGISTRY
    from scripts.update_silergy_28_jobs import SILERGY_28_POSITIONS
except ImportError:
    from data_semiconductor_jobs_part2 import SEMI_COMPANIES_PART2_REGISTRY
    from data_semiconductor_jobs_part3 import SEMI_COMPANIES_PART3_REGISTRY
    from update_silergy_28_jobs import SILERGY_28_POSITIONS

# 汇入第二部分与第三部分公司
SEMI_COMPANIES_FULL_REGISTRY.update(SEMI_COMPANIES_PART2_REGISTRY)
SEMI_COMPANIES_FULL_REGISTRY.update(SEMI_COMPANIES_PART3_REGISTRY)

# 确保矽力杰半导体具备完整28个在招岗位
SEMI_COMPANIES_FULL_REGISTRY["矽力杰半导体技术（杭州）有限公司"] = {
    "company_name": "矽力杰半导体技术（杭州）有限公司",
    "company_intro": "已上市 · 1000-9999人 · 电子/半导体/集成电路 · 全球领先的高性能模拟半导体与电源管理芯片研发龙头",
    "location_default": "杭州 · 滨江区 · 联慧街6号矽力杰产业化基地",
    "positions": SILERGY_28_POSITIONS
}

try:
    from scripts.data_silan_105_jobs import SILAN_105_POSITIONS
except ImportError:
    from data_silan_105_jobs import SILAN_105_POSITIONS

# 确保士兰微电子具备完整105个在招岗位
SEMI_COMPANIES_FULL_REGISTRY["杭州士兰微电子股份有限公司"] = {
    "company_name": "杭州士兰微电子股份有限公司",
    "company_intro": "已上市(600460) · 5000-9999人 · 半导体IDM龙头企业 · 专注于硅半导体、功率器件、集成电路及化合物半导体研发与制造",
    "location_default": "杭州 · 钱塘区 · 士兰微产业园 / 滨江区",
    "positions": SILAN_105_POSITIONS
}

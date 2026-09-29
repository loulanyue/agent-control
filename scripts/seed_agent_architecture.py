#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体架构数据初始化与落库脚本
解析两张职位截图数据：
1. 顾家家居 · 技术架构开发工程师(OA-0213B85) (media_1789916258378.png)
2. AI智能体创新团队 · AI智能体架构师 (media_1789916614145.png)
将岗位主数据与核心架构要素深度提炼落库至 MySQL。
"""

import sys
import os
import logging
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.session import sync_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS `agent_architecture_positions` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `position_title` VARCHAR(150) NOT NULL COMMENT '岗位名称',
    `company_name` VARCHAR(150) NOT NULL COMMENT '所属公司/团队',
    `company_intro` VARCHAR(500) NULL COMMENT '公司简介',
    `salary_range` VARCHAR(64) NULL COMMENT '薪资范围',
    `experience_req` VARCHAR(64) NULL COMMENT '工作经验要求',
    `education_req` VARCHAR(64) NULL COMMENT '学历要求',
    `location` VARCHAR(128) NULL COMMENT '工作地点',
    `job_responsibilities` TEXT NULL COMMENT '岗位职责',
    `job_description` TEXT NULL COMMENT '任职要求',
    `category` VARCHAR(100) NOT NULL DEFAULT '智能体架构' COMMENT '方向分类',
    `source_image` VARCHAR(255) NULL COMMENT '来源截图或链接',
    `raw_content` TEXT NOT NULL COMMENT '原始文本',
    `summary` TEXT NULL COMMENT '画像总括',
    `status` VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT '状态',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uniq_agent_arch_pos` (`company_name`, `position_title`),
    INDEX `idx_pos_title` (`position_title`),
    INDEX `idx_comp_name` (`company_name`),
    INDEX `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='智能体架构在招岗位主表';

CREATE TABLE IF NOT EXISTS `agent_architecture_requirements` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `position_id` BIGINT UNSIGNED NOT NULL COMMENT '关联岗位ID (关联 agent_architecture_positions.id)',
    `module` VARCHAR(64) NOT NULL COMMENT '一级板块',
    `dimension` VARCHAR(100) NOT NULL COMMENT '能力维度',
    `item_name` VARCHAR(255) NOT NULL COMMENT '要素核心名称',
    `item_type` ENUM('must_have', 'preferred', 'trait', 'bonus') NOT NULL DEFAULT 'must_have' COMMENT '要素性质',
    `importance_stars` TINYINT UNSIGNED NOT NULL DEFAULT 3 COMMENT '推荐星级 (1~5星)',
    `raw_text` TEXT NOT NULL COMMENT '原始描述',
    `structured_analysis` TEXT NULL COMMENT '考核要点与分析',
    `keywords` VARCHAR(255) NULL COMMENT '关键技术栈标签',
    `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序权重',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    INDEX `idx_pos_id` (`position_id`),
    INDEX `idx_module` (`module`),
    INDEX `idx_dimension` (`dimension`),
    INDEX `idx_item_type` (`item_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='智能体架构能力要素画像明细表';
"""

POSITIONS_DATA = [
    {
        "position_title": "AI智能体架构师",
        "company_name": "AI智能体创新团队",
        "company_intro": "前沿AI科技企业，专注企业级智能体自动化循环、Agent运行时Harness与复杂生产系统落地演进。",
        "salary_range": "30-50K",
        "experience_req": "3-5年",
        "education_req": "本科",
        "location": "杭州",
        "category": "AI智能体 / Agent架构",
        "source_image": "media_1789916614145.png",
        "job_responsibilities": (
            "1. 识别业务中真正适合Agent的环节，设计可控的任务循环、工具边界、数据与人工兜底，并推动上线验证。\n"
            "2. 负责系统架构和关键技术决策，覆盖状态、权限、可靠性、评测、可观测、成本与版本演进。\n"
            "3. 保持一线工程能力，承担关键模块编码、疑难故障定位、测试策略和发布质量门建设。\n"
            "4. 带领研发团队完成任务拆解、方案与代码评审、成员技术纠偏、进度和结果验收。\n"
            "5. 结合真实运行数据持续改进Agent、工程流程和团队协作方式，沉淀可复用的Harness、Skill和自动循环能力。"
        ),
        "job_description": (
            "任职要求：\n"
            "1. 本科及以上优先，计算机、软件或相关专业；第一学历、学习形式需如实说明，985/211/双一流背景同等条件优先。\n"
            "2. 7年以上软件研发经验，近期仍能亲自写核心代码、排查生产问题并设计有效测试；有成熟互联网或大型科技企业经历优先。\n"
            "3. 至少1个有真实用户或内部生产的Agent项目，能讲清控制循环、状态、Tool失败、副作用恢复、评测和发布门；仅Demo、知识问答或平台编排不等同满足。\n"
            "4. 有系统架构最终责任，能说明关键取舍、替代方案、数据与权限边界、可靠性和持续演进，不只会使用框架。\n"
            "5. 有真实研发技术带队经历，能举出任务拆解、代码/方案评审、成员纠偏和结果验收的具体事件。\n\n"
            "加分项：\n"
            "1. 有AI Coding、研发Harness、Agent运行时、评测平台或复杂工具链的生产实践。\n"
            "2. 有高并发、交易、教育、数据平台等复杂业务系统从0到1和稳定性治理经验。\n"
            "3. 有可核验的开源项目、专利、技术文章或大型团队技术影响力。\n\n"
            "补充说明：\n"
            "我们不以某个框架或模型SDK作为硬要求，更关注候选人能否判断AI边界、写出可靠系统并带队交付。"
        ),
        "raw_content": (
            "AI智能体架构师 30-50K\n"
            "杭州 | 3-5年 | 本科\n\n"
            "岗位职责：\n"
            "1.识别业务中真正适合Agent的环节，设计可控的任务循环、工具边界、数据与人工兜底，并推动上线验证。\n"
            "2.负责系统架构和关键技术决策，覆盖状态、权限、可靠性、评测、可观测、成本与版本演进。\n"
            "3.保持一线工程能力，承担关键模块编码、疑难故障定位、测试策略和发布质量门建设。\n"
            "4.带领研发团队完成任务拆解、方案与代码评审、成员技术纠偏、进度和结果验收。\n"
            "5.结合真实运行数据持续改进Agent、工程流程和团队协作方式，沉淀可复用的Harness、Skill和自动循环能力。\n\n"
            "任职要求：\n"
            "1.本科及以上优先，计算机、软件或相关专业；第一学历、学习形式需如实说明，985/211/双一流背景同等条件优先。\n"
            "2.7年以上软件研发经验，近期仍能亲自写核心代码、排查生产问题并设计有效测试；有成熟互联网或大型科技企业经历优先。\n"
            "3.至少1个有真实用户或内部生产的Agent项目，能讲清控制循环、状态、Tool失败、副作用恢复、评测和发布门；仅Demo、知识问答或平台编排不等同满足。\n"
            "4.有系统架构最终责任，能说明关键取舍、替代方案、数据与权限边界、可靠性和持续演进，不只会使用框架。\n"
            "5.有真实研发技术带队经历，能举出任务拆解、代码/方案评审、成员纠偏和结果验收的具体事件。\n\n"
            "加分项：\n"
            "1.有AI Coding、研发Harness、Agent运行时、评测平台或复杂工具链的生产实践。\n"
            "2.有高并发、交易、教育、数据平台等复杂业务系统从0到1和稳定性治理经验。\n"
            "3.有可核验的开源项目、专利、技术文章或大型团队技术影响力。\n\n"
            "补充说明：\n"
            "我们不以某个框架或模型SDK作为硬要求，更关注候选人能否判断AI边界、写出可靠系统并带队交付。"
        ),
        "summary": "负责AI Agent系统架构决策、可控任务循环与边界治理，主导Harness/Skill能力沉淀，并带领团队完成全链路工程落地。",
        "status": "active",
        "requirements": [
            {
                "module": "核心架构能力",
                "dimension": "控制循环与边界治理",
                "item_name": "可控Agent任务循环与边界设计",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "识别业务中真正适合Agent的环节，设计可控的任务循环、工具边界、数据与人工兜底，并推动上线验证。",
                "structured_analysis": "核心考查对AI边界的客观判断能力，能否在非确定性LLM与工程确定性之间建立人工兜底与约束回路。",
                "keywords": "任务循环,工具边界,人工兜底,可控循环,上线验证",
                "sort_order": 1
            },
            {
                "module": "核心架构能力",
                "dimension": "系统架构决策",
                "item_name": "系统架构与全生命周期治理",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "负责系统架构和关键技术决策，覆盖状态、权限、可靠性、评测、可观测、成本与版本演进。",
                "structured_analysis": "考查架构师级全生命周期管控能力，包括状态机治理、安全权限隔离、监控可观测性及Token成本控制。",
                "keywords": "状态机,权限边界,可靠性,评测机制,可观测性,成本治理",
                "sort_order": 2
            },
            {
                "module": "工程与代码落地",
                "dimension": "一线编码与质量门",
                "item_name": "一线核心编码与质量门禁建设",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "保持一线工程能力，承担关键模块编码、疑难故障定位、测试策略和发布质量门建设。",
                "structured_analysis": "拒绝纯PPT架构师，要求近7年持续亲手编写核心代码，能够制定自动化回归和发布门禁（Release Gate）。",
                "keywords": "核心编码,故障定位,测试策略,发布质量门,一线工程",
                "sort_order": 3
            },
            {
                "module": "项目实战经验",
                "dimension": "生产级Agent实操",
                "item_name": "生产级Agent项目闭环实战",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "至少1个有真实用户或内部生产的Agent项目，能讲清控制循环、状态、Tool失败、副作用恢复、评测和发布门；仅Demo、知识问答或平台编排不等同满足。",
                "structured_analysis": "深度检验真实生产掉坑与解决经验，对Tool调用失败重试、上下文副作用回滚机制有严密方案。",
                "keywords": "真实生产项目,Tool失败恢复,副作用回滚,评测闭环,反Demo",
                "sort_order": 4
            },
            {
                "module": "技术带队能力",
                "dimension": "研发管理与技术纠偏",
                "item_name": "研发团队任务拆解与代码评审",
                "item_type": "must_have",
                "importance_stars": 4,
                "raw_text": "带领研发团队完成任务拆解、方案与代码评审、成员技术纠偏、进度和结果验收。",
                "structured_analysis": "考查技术领导力，包括复杂目标拆解落地、高标准Code Review及对团队方向的技术纠偏能力。",
                "keywords": "任务拆解,代码评审,技术纠偏,进度把控,结果验收",
                "sort_order": 5
            },
            {
                "module": "进阶技术壁垒",
                "dimension": "运行时与工具链",
                "item_name": "AI Coding与Harness生产实践",
                "item_type": "bonus",
                "importance_stars": 5,
                "raw_text": "有AI Coding、研发Harness、Agent运行时、评测平台或复杂工具链的生产实践。",
                "structured_analysis": "具备自研或深入改造 Agent 执行基座（Harness）与复杂工具链的能力，能支撑模型能力最大化释放。",
                "keywords": "AI Coding,Harness基座,Agent运行时,评测平台,复杂工具链",
                "sort_order": 6
            }
        ]
    },
    {
        "position_title": "技术架构开发工程师(OA-0213B85)",
        "company_name": "顾家家居",
        "company_intro": "顾家家居股份有限公司，享誉全球的知名大家居品牌，致力于为全球家庭提供健康、舒适、环保的家居解决方案。",
        "salary_range": "22-30K·14薪",
        "experience_req": "5-10年",
        "education_req": "本科",
        "location": "杭州 · 上城区",
        "category": "技术架构 / MES企业架构",
        "source_image": "media_1789916258378.png",
        "job_responsibilities": (
            "1、负责 MES 等核心业务系统的产品规划、需求拆解、功能模块详细设计，主导核心代码编写与关键功能实现。\n"
            "2、负责技术研发落地与技术难点攻关，保障系统高可用、高稳定、易扩展，持续优化系统性能与架构合理性。\n"
            "3、负责核心项目的技术架构选型、整体架构设计、技术规划与方案落地，把控系统技术方向与架构质量。\n"
            "4、参与代码评审、技术规范制定，推动团队研发效率与代码质量提升。"
        ),
        "job_description": (
            "任职要求：\n"
            "1、具备扎实的 Java 开发基础，精通 Web 开发相关技术栈，熟练使用主流开源框架与中间件。\n"
            "2、精通 SQL 编写与数据库性能优化，熟练使用 MySQL、Oracle 等关系型数据库，具备数据库调优实战经验。\n"
            "3、具备良好的系统设计能力、问题排查能力与工程化思维，能独立完成复杂模块设计与开发。\n"
            "4、有主导 MES 系统架构设计、核心代码开发及项目落地经验者优先。\n"
            "熟悉金蝶云苍穹平台，具备苍穹低代码开发、平台定制化开发实战经验者优先。\n\n"
            "工作地址：杭州上城区顾家大厦东宁路599号\n"
            "招聘者：金女士 · 招聘者"
        ),
        "raw_content": (
            "技术架构开发工程师(OA-0213B85) 22-30K·14薪\n"
            "杭州 | 5-10年 | 本科\n"
            "招聘者：金女士 · 招聘者 (顾家家居)\n"
            "工作地址：杭州上城区顾家大厦东宁路599号\n\n"
            "岗位职责：\n"
            "1、负责 MES 等核心业务系统的产品规划、需求拆解、功能模块详细设计，主导核心代码编写与关键功能实现。\n"
            "2、负责技术研发落地与技术难点攻关，保障系统高可用、高稳定、易扩展，持续优化系统性能与架构合理性。\n"
            "3、负责核心项目的技术架构选型、整体架构设计、技术规划与方案落地，把控系统技术方向与架构质量。\n"
            "4、参与代码评审、技术规范制定，推动团队研发效率与代码质量提升。\n\n"
            "任职要求：\n"
            "1、具备扎实的 Java 开发基础，精通 Web 开发相关技术栈，熟练使用主流开源框架与中间件。\n"
            "2、精通 SQL 编写与数据库性能优化，熟练使用 MySQL、Oracle 等关系型数据库，具备数据库调优实战经验。\n"
            "3、具备良好的系统设计能力、问题排查能力与工程化思维，能独立完成复杂模块设计与开发。\n"
            "4、有主导 MES 系统架构设计、核心代码开发及项目落地经验者优先。\n"
            "熟悉金蝶云苍穹平台，具备苍穹低代码开发、平台定制化开发实战经验者优先。"
        ),
        "summary": "负责顾家家居MES制造核心业务系统技术架构设计、架构选型与高可用方案落地，主导Java核心编码与苍穹平台集成。",
        "status": "active",
        "requirements": [
            {
                "module": "核心架构能力",
                "dimension": "业务系统架构设计",
                "item_name": "MES核心业务架构规划与技术选型",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "负责核心项目的技术架构选型、整体架构设计、技术规划与方案落地，把控系统技术方向与架构质量；有主导 MES 系统架构设计经验者优先。",
                "structured_analysis": "要求具备工业制造核心 MES 系统架构规划实战，能从需求拆解、模块设计到高可用落地全生命周期把控。",
                "keywords": "MES系统,架构选型,技术规划,高可用,系统扩展性",
                "sort_order": 1
            },
            {
                "module": "技术栈能力",
                "dimension": "Java与中间件",
                "item_name": "Java全栈与主流开源中间件精通",
                "item_type": "must_have",
                "importance_stars": 5,
                "raw_text": "具备扎实的 Java 开发基础，精通 Web 开发相关技术栈，熟练使用主流开源框架与中间件。",
                "structured_analysis": "熟练使用 Spring 生态、微服务组件、分布式缓存与消息队列等，具备扎实的系统编码能力与设计模式素养。",
                "keywords": "Java,Web技术栈,开源框架,中间件,分布式",
                "sort_order": 2
            },
            {
                "module": "数据工程能力",
                "dimension": "数据库与性能调优",
                "item_name": "关系型数据库高精调优与SQL优化",
                "item_type": "must_have",
                "importance_stars": 4,
                "raw_text": "精通 SQL 编写与数据库性能优化，熟练使用 MySQL、Oracle 等关系型数据库，具备数据库调优实战经验。",
                "structured_analysis": "要求掌握执行计划分析、索引调优、锁与事务机制，能应对制造海量数据并发写入与复杂统计查询场景。",
                "keywords": "SQL性能优化,MySQL,Oracle,数据库调优,事务与索引",
                "sort_order": 3
            },
            {
                "module": "平台化与低代码",
                "dimension": "企业云平台定制",
                "item_name": "金蝶云苍穹平台定制与低代码开发",
                "item_type": "preferred",
                "importance_stars": 4,
                "raw_text": "熟悉金蝶云苍穹平台，具备苍穹低代码开发、平台定制化开发实战经验者优先。",
                "structured_analysis": "掌握企业级苍穹平台开发框架、元数据模型驱动及低代码与复杂客开结合的设计模式。",
                "keywords": "金蝶云苍穹,低代码开发,平台定制化,企业中台",
                "sort_order": 4
            },
            {
                "module": "工程管理与规范",
                "dimension": "研发规范与团队提效",
                "item_name": "技术规范制定与代码评审把控",
                "item_type": "must_have",
                "importance_stars": 4,
                "raw_text": "参与代码评审、技术规范制定，推动团队研发效率与代码质量提升；具备良好的系统设计能力与工程化思维。",
                "structured_analysis": "通过规范落地、架构把控与深度 Code Review 带领团队高质量交付，杜绝技术债务堆积。",
                "keywords": "代码评审,技术规范,工程化思维,研发效率,架构把关",
                "sort_order": 5
            }
        ]
    }
]

def seed():
    logger.info("开始执行智能体架构数据表初始化与数据落库...")
    with sync_engine.begin() as conn:
        # 1. 创建表结构
        for stmt in CREATE_TABLES_SQL.strip().split(";"):
            sql_clean = stmt.strip()
            if sql_clean:
                conn.execute(text(sql_clean))
        logger.info("表结构 agent_architecture_positions 和 agent_architecture_requirements 检查/创建完成。")

        # 2. 插入岗位数据与能力要素
        for p in POSITIONS_DATA:
            reqs = p.pop("requirements", [])
            # 查找或插入主表
            check_sql = text("""
                SELECT id FROM agent_architecture_positions
                WHERE company_name = :company_name AND position_title = :position_title
            """)
            existing_id = conn.execute(check_sql, {
                "company_name": p["company_name"],
                "position_title": p["position_title"]
            }).scalar()

            if existing_id:
                logger.info(f"更新已有架构岗位 [{existing_id}] {p['company_name']} - {p['position_title']}")
                update_sql = text("""
                    UPDATE agent_architecture_positions SET
                        company_intro = :company_intro,
                        salary_range = :salary_range,
                        experience_req = :experience_req,
                        education_req = :education_req,
                        location = :location,
                        job_responsibilities = :job_responsibilities,
                        job_description = :job_description,
                        category = :category,
                        source_image = :source_image,
                        raw_content = :raw_content,
                        summary = :summary,
                        status = :status,
                        updated_at = NOW()
                    WHERE id = :id
                """)
                params = {**p, "id": existing_id}
                conn.execute(update_sql, params)
                pos_id = existing_id
            else:
                insert_sql = text("""
                    INSERT INTO agent_architecture_positions (
                        position_title, company_name, company_intro, salary_range,
                        experience_req, education_req, location, job_responsibilities,
                        job_description, category, source_image, raw_content, summary, status
                    ) VALUES (
                        :position_title, :company_name, :company_intro, :salary_range,
                        :experience_req, :education_req, :location, :job_responsibilities,
                        :job_description, :category, :source_image, :raw_content, :summary, :status
                    )
                """)
                conn.execute(insert_sql, p)
                pos_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
                logger.info(f"新增架构岗位 [{pos_id}] {p['company_name']} - {p['position_title']}")

            # 插入或更新能力要素
            # 先清空该岗位已存在的旧要素，保证幂等更新
            conn.execute(text("DELETE FROM agent_architecture_requirements WHERE position_id = :pos_id"), {"pos_id": pos_id})
            for r in reqs:
                insert_req = text("""
                    INSERT INTO agent_architecture_requirements (
                        position_id, module, dimension, item_name, item_type,
                        importance_stars, raw_text, structured_analysis, keywords, sort_order
                    ) VALUES (
                        :position_id, :module, :dimension, :item_name, :item_type,
                        :importance_stars, :raw_text, :structured_analysis, :keywords, :sort_order
                    )
                """)
                r_params = {**r, "position_id": pos_id}
                conn.execute(insert_req, r_params)
            logger.info(f"岗位 [{pos_id}] 成功落库 {len(reqs)} 条架构能力要素画像。")

        # 统计总数
        cnt_pos = conn.execute(text("SELECT COUNT(*) FROM agent_architecture_positions")).scalar()
        cnt_req = conn.execute(text("SELECT COUNT(*) FROM agent_architecture_requirements")).scalar()
        logger.info(f"✅ 智能体架构数据落库完成！当前在招岗位数: {cnt_pos}，能力画像要素数: {cnt_req}")

if __name__ == "__main__":
    seed()

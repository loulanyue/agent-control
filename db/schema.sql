-- =============================================================================
-- Agent Control Database Schema (Full 34 Tables)
-- Generated & Recovered from MySQL binlog
-- Database: agent_control
-- =============================================================================

CREATE DATABASE IF NOT EXISTS `agent_control` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `agent_control`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for agents
-- ----------------------------
CREATE TABLE `agents` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `name` varchar(120) NOT NULL,
  `agent_type` varchar(80) NOT NULL DEFAULT 'generic',
  `capabilities` json NOT NULL,
  `metadata` json NOT NULL,
  `status` enum('online','offline','busy','disabled') NOT NULL DEFAULT 'offline',
  `last_seen_at` datetime(3) DEFAULT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`)
) ENGINE=InnoDB AUTO_INCREMENT=76 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for api_clients
-- ----------------------------
CREATE TABLE `api_clients` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `name` varchar(120) NOT NULL,
  `token_hash` char(64) NOT NULL,
  `scopes` json NOT NULL,
  `last_used_at` datetime(3) DEFAULT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `token_hash` (`token_hash`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for bitcoin_mining_runs
-- ----------------------------
CREATE TABLE IF NOT EXISTS bitcoin_mining_runs (
      id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      mode VARCHAR(32) NOT NULL DEFAULT 'simulation',
      pool_host VARCHAR(128) DEFAULT NULL,
      pool_port INT DEFAULT NULL,
      wallet_address VARCHAR(128) DEFAULT NULL,
      threads INT UNSIGNED DEFAULT 1,
      hashrate_khs DOUBLE UNSIGNED DEFAULT 0,
      total_hashes BIGINT UNSIGNED DEFAULT 0,
      valid_shares INT UNSIGNED DEFAULT 0,
      blocks_found INT UNSIGNED DEFAULT 0,
      cpu_usage_pct FLOAT DEFAULT 0,
      duration_seconds INT UNSIGNED DEFAULT 0,
      status VARCHAR(32) NOT NULL DEFAULT 'COMPLETED',
      log_file VARCHAR(256),
      run_time DATETIME NOT NULL,
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
;

-- ----------------------------
-- Table structure for github_contributions
-- ----------------------------
CREATE TABLE IF NOT EXISTS `github_contributions` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `pr_url` VARCHAR(512) NOT NULL COMMENT 'PR完整链接或Security Advisory URL',
    `repo_name` VARCHAR(128) NOT NULL COMMENT '仓库全名(如 browser-use/browser-use)',
    `repo_owner` VARCHAR(64) NOT NULL COMMENT '仓库拥有者',
    `repo_stars` VARCHAR(32) NULL DEFAULT '' COMMENT '仓库Star数(如 110.4k★)',
    `pr_number` INT NULL COMMENT 'PR编号',
    `pr_title` VARCHAR(512) NULL DEFAULT '' COMMENT 'PR标题',
    `branch_name` VARCHAR(128) NULL DEFAULT '' COMMENT '特性分支名',
    `category` VARCHAR(64) NULL DEFAULT '' COMMENT '分类板块',
    `conclusion` TEXT NOT NULL COMMENT '结论与根因修复摘要',
    `is_security` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否为安全披露(0=否, 1=是)',
    `ghsa_id` VARCHAR(64) NULL DEFAULT '' COMMENT '安全通告编号(如 GHSA-jfrj-h562-fggm)',
    `status` VARCHAR(32) NOT NULL DEFAULT 'OPEN' COMMENT '状态: OPEN, MERGED, CLOSED',
    `merged_at` DATETIME NULL COMMENT '合并时间',
    `log_file` VARCHAR(256) NOT NULL COMMENT '关联日志文件相对路径',
    `run_time` DATETIME NOT NULL COMMENT '执行时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '首次入库时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近更新时间',
    
    UNIQUE KEY `uk_pr_url` (`pr_url`(255)),
    KEY `idx_repo_name` (`repo_name`),
    KEY `idx_repo_owner` (`repo_owner`),
    KEY `idx_status` (`status`),
    KEY `idx_run_time` (`run_time`),
    KEY `idx_is_security` (`is_security`),
    KEY `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='GitHub 开源贡献与PR记录表'
;

-- ----------------------------
-- Table structure for github_prs_lifecycle
-- ----------------------------
CREATE TABLE IF NOT EXISTS github_prs_lifecycle (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    repo_name VARCHAR(128) NOT NULL,
    repo_owner VARCHAR(64) NOT NULL,
    pr_number INT NOT NULL,
    title VARCHAR(512) NOT NULL,
    state VARCHAR(32) NOT NULL COMMENT 'MERGED, OPEN, CLOSED',
    created_at DATETIME NULL,
    updated_at DATETIME NULL,
    closed_at DATETIME NULL,
    merged_at DATETIME NULL,
    pr_url VARCHAR(512) NOT NULL UNIQUE,
    branch_name VARCHAR(128) NULL,
    mergeable_status VARCHAR(32) DEFAULT 'UNKNOWN' COMMENT 'MERGEABLE, CONFLICTING, UNKNOWN',
    review_decision VARCHAR(32) DEFAULT 'NONE' COMMENT 'APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED, NONE',
    category VARCHAR(64) DEFAULT 'upstream' COMMENT 'upstream, self_owned',
    last_sync_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_state (state),
    INDEX idx_repo (repo_name),
    INDEX idx_owner (repo_owner),
    INDEX idx_category (category),
    INDEX idx_mergeable (mergeable_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
;

-- ----------------------------
-- Table structure for graph_approvals
-- ----------------------------
CREATE TABLE `graph_approvals` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `node_run_id` bigint unsigned NOT NULL,
  `decision` enum('approved','rejected') NOT NULL,
  `operator_id` varchar(120) NOT NULL,
  `opinion` text,
  `idempotency_key` varchar(190) NOT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uq_graph_approval_node` (`node_run_id`),
  UNIQUE KEY `uq_graph_approval_idempotency` (`idempotency_key`),
  CONSTRAINT `fk_graph_approval_node_run` FOREIGN KEY (`node_run_id`) REFERENCES `graph_node_runs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for graph_definitions
-- ----------------------------
CREATE TABLE `graph_definitions` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `name` varchar(180) NOT NULL,
  `description` text,
  `tags` json NOT NULL,
  `status` enum('draft','published','disabled') NOT NULL DEFAULT 'draft',
  `current_draft_version_id` bigint unsigned DEFAULT NULL,
  `current_published_version_id` bigint unsigned DEFAULT NULL,
  `created_by` varchar(120) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `deleted_by` varchar(120) DEFAULT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `idx_graph_definitions_status` (`deleted_at`,`status`,`updated_at`),
  KEY `fk_graph_current_draft` (`current_draft_version_id`),
  KEY `fk_graph_current_published` (`current_published_version_id`),
  CONSTRAINT `fk_graph_current_draft` FOREIGN KEY (`current_draft_version_id`) REFERENCES `graph_versions` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_graph_current_published` FOREIGN KEY (`current_published_version_id`) REFERENCES `graph_versions` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for graph_edges
-- ----------------------------
CREATE TABLE `graph_edges` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `version_id` bigint unsigned NOT NULL,
  `edge_key` varchar(100) NOT NULL,
  `source_node_key` varchar(80) NOT NULL,
  `target_node_key` varchar(80) NOT NULL,
  `source_port` varchar(80) DEFAULT NULL,
  `target_port` varchar(80) DEFAULT NULL,
  `condition_config` json NOT NULL,
  `data_mapping` json NOT NULL,
  `permission_config` json NOT NULL,
  `sort_order` int NOT NULL DEFAULT '0',
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uq_graph_edge_key` (`version_id`,`edge_key`),
  KEY `idx_graph_edge_source` (`version_id`,`source_node_key`),
  KEY `idx_graph_edge_target` (`version_id`,`target_node_key`),
  CONSTRAINT `fk_graph_edge_version` FOREIGN KEY (`version_id`) REFERENCES `graph_versions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for graph_node_runs
-- ----------------------------
CREATE TABLE `graph_node_runs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `run_id` bigint unsigned NOT NULL,
  `node_id` bigint unsigned NOT NULL,
  `node_key` varchar(80) NOT NULL,
  `instance_key` varchar(120) NOT NULL DEFAULT 'default',
  `status` enum('waiting','ready','queued','claimed','running','blocked','validating','retry_wait','completed','failed','skipped','cancelled') NOT NULL DEFAULT 'waiting',
  `input_data` json NOT NULL,
  `output_data` json NOT NULL,
  `checkpoint` json NOT NULL,
  `task_id` bigint unsigned DEFAULT NULL,
  `retry_count` int unsigned NOT NULL DEFAULT '0',
  `error_message` text,
  `started_at` datetime(3) DEFAULT NULL,
  `finished_at` datetime(3) DEFAULT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uq_graph_node_run_instance` (`run_id`,`node_key`,`instance_key`),
  UNIQUE KEY `uq_graph_node_run_task` (`task_id`),
  KEY `idx_graph_node_runs_ready` (`status`,`updated_at`),
  KEY `idx_graph_node_runs_run` (`run_id`,`status`),
  KEY `fk_graph_node_run_node` (`node_id`),
  CONSTRAINT `fk_graph_node_run` FOREIGN KEY (`run_id`) REFERENCES `graph_runs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_graph_node_run_node` FOREIGN KEY (`node_id`) REFERENCES `graph_nodes` (`id`),
  CONSTRAINT `fk_graph_node_run_task` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for graph_nodes
-- ----------------------------
CREATE TABLE `graph_nodes` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `version_id` bigint unsigned NOT NULL,
  `node_key` varchar(80) NOT NULL,
  `node_type` enum('start','agent','validator','approval','join','tool','code','orchestrator','subgraph','end') NOT NULL,
  `label` varchar(180) NOT NULL,
  `position_x` decimal(12,3) NOT NULL DEFAULT '0.000',
  `position_y` decimal(12,3) NOT NULL DEFAULT '0.000',
  `input_schema` json NOT NULL,
  `output_schema` json NOT NULL,
  `config` json NOT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uq_graph_node_key` (`version_id`,`node_key`),
  CONSTRAINT `fk_graph_node_version` FOREIGN KEY (`version_id`) REFERENCES `graph_versions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for graph_run_events
-- ----------------------------
CREATE TABLE `graph_run_events` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `run_id` bigint unsigned NOT NULL,
  `node_run_id` bigint unsigned DEFAULT NULL,
  `event_key` varchar(190) DEFAULT NULL,
  `event_type` varchar(100) NOT NULL,
  `actor_type` enum('user','agent','scheduler','system') NOT NULL,
  `actor_id` varchar(120) DEFAULT NULL,
  `from_status` varchar(40) DEFAULT NULL,
  `to_status` varchar(40) DEFAULT NULL,
  `payload` json NOT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uq_graph_run_event_key` (`run_id`,`event_key`),
  KEY `idx_graph_run_events_timeline` (`run_id`,`created_at`),
  KEY `fk_graph_event_node_run` (`node_run_id`),
  CONSTRAINT `fk_graph_event_node_run` FOREIGN KEY (`node_run_id`) REFERENCES `graph_node_runs` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_graph_event_run` FOREIGN KEY (`run_id`) REFERENCES `graph_runs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for graph_runs
-- ----------------------------
CREATE TABLE `graph_runs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `graph_id` bigint unsigned NOT NULL,
  `version_id` bigint unsigned NOT NULL,
  `parent_node_run_id` bigint unsigned DEFAULT NULL,
  `status` enum('queued','running','paused','completed','failed','cancelled') NOT NULL DEFAULT 'queued',
  `trigger_type` enum('manual','api','schedule','graph') NOT NULL DEFAULT 'manual',
  `trigger_id` varchar(190) DEFAULT NULL,
  `idempotency_key` varchar(190) DEFAULT NULL,
  `input_data` json NOT NULL,
  `state_data` json NOT NULL,
  `execution_policy` json NOT NULL,
  `summary` text,
  `error_message` text,
  `started_at` datetime(3) DEFAULT NULL,
  `finished_at` datetime(3) DEFAULT NULL,
  `paused_at` datetime(3) DEFAULT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uq_graph_run_idempotency` (`graph_id`,`idempotency_key`),
  KEY `idx_graph_runs_status` (`status`,`updated_at`),
  KEY `idx_graph_runs_definition` (`graph_id`,`created_at`),
  KEY `fk_graph_run_version` (`version_id`),
  KEY `fk_graph_run_parent_node` (`parent_node_run_id`),
  CONSTRAINT `fk_graph_run_definition` FOREIGN KEY (`graph_id`) REFERENCES `graph_definitions` (`id`),
  CONSTRAINT `fk_graph_run_parent_node` FOREIGN KEY (`parent_node_run_id`) REFERENCES `graph_node_runs` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_graph_run_version` FOREIGN KEY (`version_id`) REFERENCES `graph_versions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for graph_versions
-- ----------------------------
CREATE TABLE `graph_versions` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `graph_id` bigint unsigned NOT NULL,
  `version_no` int unsigned NOT NULL,
  `status` enum('draft','published','archived') NOT NULL DEFAULT 'draft',
  `graph_schema` json NOT NULL,
  `execution_policy` json NOT NULL,
  `validation_result` json NOT NULL,
  `content_hash` char(64) DEFAULT NULL,
  `revision` int unsigned NOT NULL DEFAULT '1',
  `published_at` datetime(3) DEFAULT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uq_graph_version` (`graph_id`,`version_no`),
  KEY `idx_graph_versions_status` (`graph_id`,`status`,`version_no`),
  CONSTRAINT `fk_graph_version_definition` FOREIGN KEY (`graph_id`) REFERENCES `graph_definitions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for hz_notice_crawl_runs
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hz_notice_crawl_runs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `crawl_batch` VARCHAR(32) NOT NULL COMMENT '批次号(YYYYMMDD_HHmm)',
    `total_fetched` INT NOT NULL DEFAULT 0 COMMENT '抓取总数',
    `personal_count` INT NOT NULL DEFAULT 0 COMMENT '个人公示数量',
    `list_count` INT NOT NULL DEFAULT 0 COMMENT '清单公示数量',
    `success_count` INT NOT NULL DEFAULT 0 COMMENT '成功详情数',
    `error_count` INT NOT NULL DEFAULT 0 COMMENT '失败详情数',
    `status` VARCHAR(32) NOT NULL DEFAULT 'SUCCESS' COMMENT '执行状态: SUCCESS, FAILED',
    `error_message` TEXT NULL COMMENT '错误信息',
    `started_at` DATETIME NOT NULL COMMENT '任务开始时间',
    `finished_at` DATETIME NULL COMMENT '任务结束时间',
    `duration_sec` FLOAT NOT NULL DEFAULT 0 COMMENT '耗时(秒)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY `uk_crawl_batch` (`crawl_batch`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='杭州人才会客厅-爬取批次日志表'
;

-- ----------------------------
-- Table structure for hz_talent_notices
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hz_talent_notices` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `notice_id` VARCHAR(64) NOT NULL COMMENT '公示唯一标识(URL中的no参数)',
    `notice_type` ENUM('personal', 'list') NOT NULL DEFAULT 'personal' COMMENT '公示类型: personal(个人公示), list(清单类公示)',
    `title` VARCHAR(512) NOT NULL COMMENT '公示标题',
    `publish_date` DATE NULL COMMENT '发布日期',
    `detail_url` VARCHAR(512) NOT NULL COMMENT '详情页完整URL',
    `author` VARCHAR(128) NULL DEFAULT '' COMMENT '作者/发布单位',
    `wenhao` VARCHAR(128) NULL DEFAULT '' COMMENT '文号',
    
    -- 个人公示结构化字段
    `person_name` VARCHAR(128) NULL DEFAULT '' COMMENT '申报人姓名',
    `gender` VARCHAR(16) NULL DEFAULT '' COMMENT '性别',
    `birth_date` VARCHAR(32) NULL DEFAULT '' COMMENT '出生年月',
    `work_unit` VARCHAR(256) NULL DEFAULT '' COMMENT '工作单位',
    `accept_dept` VARCHAR(256) NULL DEFAULT '' COMMENT '受理部门',
    `apply_type` VARCHAR(512) NULL DEFAULT '' COMMENT '申报人才类型',
    `publicity_period` VARCHAR(128) NULL DEFAULT '' COMMENT '公示时间段',
    
    -- 正文内容与HTML
    `content_text` LONGTEXT NULL COMMENT '正文纯文本',
    `content_html` LONGTEXT NULL COMMENT '原始HTML正文',
    
    -- 批次与时间戳
    `crawl_batch` VARCHAR(32) NOT NULL COMMENT '首次抓取批次号(YYYYMMDD_HHmm)',
    `last_crawl_batch` VARCHAR(32) NOT NULL COMMENT '最近一次更新批次号',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '首次入库时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近更新时间',
    
    UNIQUE KEY `uk_notice_id` (`notice_id`),
    KEY `idx_publish_date` (`publish_date`),
    KEY `idx_work_unit` (`work_unit`(128)),
    KEY `idx_person_name` (`person_name`),
    KEY `idx_notice_type` (`notice_type`),
    KEY `idx_crawl_batch` (`crawl_batch`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='杭州人才会客厅-公示公告明细表'
;

-- ----------------------------
-- Table structure for hf_talent_crawl_runs
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hf_talent_crawl_runs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `crawl_batch` VARCHAR(32) NOT NULL COMMENT '批次号(YYYYMMDD_HHmm)',
    `total_fetched` INT NOT NULL DEFAULT 0 COMMENT '拉取列表总数',
    `publicity_count` INT NOT NULL DEFAULT 0 COMMENT '公示条数',
    `result_count` INT NOT NULL DEFAULT 0 COMMENT '结果条数',
    `success_count` INT NOT NULL DEFAULT 0 COMMENT '成功入库数',
    `error_count` INT NOT NULL DEFAULT 0 COMMENT '失败详情数',
    `status` VARCHAR(32) NOT NULL DEFAULT 'SUCCESS' COMMENT '状态: RUNNING, SUCCESS, FAILED',
    `error_message` TEXT NULL COMMENT '报错信息',
    `started_at` DATETIME NOT NULL COMMENT '开始时间',
    `finished_at` DATETIME NULL COMMENT '结束时间',
    `duration_sec` FLOAT NOT NULL DEFAULT 0 COMMENT '耗时(秒)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY `uk_hf_crawl_batch` (`crawl_batch`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='合肥人才认定爬取批次日志表';

-- ----------------------------
-- Table structure for hf_talent_records
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hf_talent_records` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `record_id` VARCHAR(64) NOT NULL COMMENT '官方唯一标识(公示为id, 结果为talentId)',
    `record_type` ENUM('publicity', 'result') NOT NULL COMMENT '数据类型: publicity(认定公示), result(认定结果)',
    `title` VARCHAR(512) NOT NULL COMMENT '标题',
    `publish_date` DATE NULL COMMENT '公示发布日期/认定日期',
    `detail_url` VARCHAR(512) NOT NULL COMMENT '详情页URL',
    `author` VARCHAR(128) NULL DEFAULT '合肥市人力资源和社会保障局 合肥市人才办' COMMENT '发布单位',
    
    -- 核心人员与单位信息 (经 getPublicInfoById 去脱敏真实数据)
    `person_name` VARCHAR(128) NOT NULL COMMENT '真实姓名(去脱敏)',
    `person_name_masked` VARCHAR(128) NULL DEFAULT '' COMMENT '列表脱敏姓名(如孙*玲)',
    `gender` VARCHAR(16) NULL DEFAULT '' COMMENT '性别',
    `work_unit` VARCHAR(256) NULL DEFAULT '' COMMENT '工作单位(companyName)',
    `accept_dept` VARCHAR(256) NULL DEFAULT '' COMMENT '受理部门(acceptanceName)',
    
    -- 人才级别与申报类别
    `level_code` VARCHAR(32) NULL DEFAULT '' COMMENT '等级编号(1/2/3/4...)',
    `level_code_name` VARCHAR(64) NULL DEFAULT '' COMMENT '人才级别(A类/B类/C类/D类/E类等)',
    `clause` VARCHAR(512) NULL DEFAULT '' COMMENT '认定条款/依据',
    `talent_type` VARCHAR(32) NULL DEFAULT '' COMMENT '人才类型代码',
    `talent_type_name` VARCHAR(128) NULL DEFAULT '' COMMENT '人才类型名称(如全职人才)',
    
    -- 时间周期
    `publicity_start_time` DATETIME NULL COMMENT '公示开始时间',
    `publicity_end_time` DATETIME NULL COMMENT '公示结束时间',
    `publicity_period` VARCHAR(128) NULL DEFAULT '' COMMENT '公示周期文本描述',
    `confirm_time` DATETIME NULL COMMENT '认定确认时间',
    
    -- 审批联系机构
    `approval_name` VARCHAR(128) NULL DEFAULT '' COMMENT '审批单位',
    `approval_tel` VARCHAR(64) NULL DEFAULT '' COMMENT '审批电话',
    `approval_review_name` VARCHAR(128) NULL DEFAULT '' COMMENT '复核单位',
    `approval_review_tel` VARCHAR(64) NULL DEFAULT '' COMMENT '复核电话',
    
    -- 正文内容与原始数据
    `content_text` LONGTEXT NULL COMMENT '官方规范正文纯文本',
    `raw_json` JSON NULL COMMENT '原始详情JSON对象',
    
    -- 批次与时间戳
    `crawl_batch` VARCHAR(32) NOT NULL COMMENT '首次抓取批次号',
    `last_crawl_batch` VARCHAR(32) NOT NULL COMMENT '最近一次更新批次号',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY `uk_record_id` (`record_id`),
    KEY `idx_record_type` (`record_type`),
    KEY `idx_publish_date` (`publish_date`),
    KEY `idx_person_name` (`person_name`),
    KEY `idx_work_unit` (`work_unit`(128)),
    KEY `idx_level_code_name` (`level_code_name`),
    KEY `idx_crawl_batch` (`crawl_batch`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='合肥人才认定公示与结果明细表';


-- ----------------------------
-- Table structure for idempotency_keys
-- ----------------------------
CREATE TABLE `idempotency_keys` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `client_id` bigint unsigned NOT NULL,
  `idempotency_key` varchar(190) NOT NULL,
  `request_hash` char(64) NOT NULL,
  `status_code` smallint unsigned NOT NULL,
  `response_body` json NOT NULL,
  `expires_at` datetime(3) NOT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_idempotency` (`client_id`,`idempotency_key`),
  KEY `idx_idempotency_expiry` (`expires_at`),
  CONSTRAINT `fk_idempotency_client` FOREIGN KEY (`client_id`) REFERENCES `api_clients` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for job_positions
-- ----------------------------
CREATE TABLE IF NOT EXISTS `job_positions` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `position_title` VARCHAR(150) NOT NULL COMMENT '岗位名称 (如: AI Native 研发工程师 / AI Agent 工程师)',
    `company_name` VARCHAR(150) NOT NULL DEFAULT '杭州积海半导体有限公司' COMMENT '所属公司名称',
    `company_intro` VARCHAR(500) NULL COMMENT '公司简介 / 规模与行业',
    `salary_range` VARCHAR(64) NULL COMMENT '薪资范围 (如: 28-35K · 14薪)',
    `experience_req` VARCHAR(64) NULL COMMENT '工作经验要求 (如: 5-10年)',
    `education_req` VARCHAR(64) NULL COMMENT '学历要求 (如: 本科)',
    `location` VARCHAR(128) NULL COMMENT '工作地点 (如: 杭州 · 钱塘区 · 大江东)',
    `job_responsibilities` TEXT NULL COMMENT '岗位工作职责详细列表',
    `job_description` TEXT NULL COMMENT '任职要求 / 职位详细描述',
    `category` VARCHAR(100) NOT NULL DEFAULT 'AI Agent' COMMENT '岗位方向类别',
    `source_image` VARCHAR(255) NOT NULL DEFAULT 'media_1788048860408.png' COMMENT '所属来源图片文件名或URL',
    `raw_content` TEXT NOT NULL COMMENT 'JD 完整原始文本',
    `summary` TEXT NULL COMMENT '要素总括 / 一句话画像',
    `status` VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT '状态',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    INDEX `idx_position_title` (`position_title`),
    INDEX `idx_company_name` (`company_name`),
    INDEX `idx_source_image` (`source_image`),
    INDEX `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='职位招聘信息主表'
;

-- ----------------------------
-- Table structure for job_requirements
-- ----------------------------
CREATE TABLE IF NOT EXISTS `job_requirements` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `position_id` BIGINT UNSIGNED NOT NULL COMMENT '关联岗位ID (关联 job_positions.id)',
    `module` VARCHAR(64) NOT NULL COMMENT '一级板块 (基础条件, 专业能力, 能力特质, 加分项)',
    `dimension` VARCHAR(100) NOT NULL COMMENT '能力维度/分类',
    `item_name` VARCHAR(255) NOT NULL COMMENT '要素核心名称',
    `item_type` ENUM('must_have', 'preferred', 'trait', 'bonus') NOT NULL DEFAULT 'must_have' COMMENT '要素性质: must_have(必备/基础), preferred(优先), trait(软特质/素养), bonus(加分项)',
    `importance_stars` TINYINT UNSIGNED NOT NULL DEFAULT 3 COMMENT '重要程度/推荐星级 (1~5星)',
    `raw_text` TEXT NOT NULL COMMENT '原始要素描述',
    `structured_analysis` TEXT NULL COMMENT '要素深度拆解与考核要点',
    `keywords` VARCHAR(255) NULL COMMENT '关键技术栈/关键词',
    `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序权重',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    INDEX `idx_position_id` (`position_id`),
    INDEX `idx_module` (`module`),
    INDEX `idx_dimension` (`dimension`),
    INDEX `idx_item_type` (`item_type`),
    INDEX `idx_importance` (`importance_stars`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='职位要求完整要素明细表'
;

-- ----------------------------
-- Table structure for part_time_opportunities
-- ----------------------------
CREATE TABLE IF NOT EXISTS `part_time_opportunities` (
    `opportunity_id` VARCHAR(128) NOT NULL PRIMARY KEY COMMENT '稳定唯一主键(如 outlier:general-coding)',
    `platform` VARCHAR(64) NOT NULL COMMENT '平台来源(如 outlier, opentrain, mindrift)',
    `title` VARCHAR(512) NOT NULL COMMENT '机会/岗位标题',
    `url` VARCHAR(512) NOT NULL COMMENT '申请或详情链接',
    `status` ENUM('active', 'watchlist', 'excluded', 'applied') NOT NULL DEFAULT 'active' COMMENT '状态: active(活跃可行动), watchlist(观察队列), excluded(已排除), applied(已申请)',
    `priority` VARCHAR(16) NULL DEFAULT 'P3' COMMENT '优先级(P0, P1, P2, P3)',
    `score` INT NOT NULL DEFAULT 0 COMMENT '综合评分(0-100)',
    `payout_info` TEXT NULL COMMENT '收益/时薪信息说明',
    `payout_speed` VARCHAR(128) NULL DEFAULT '' COMMENT '预计启动与收款周期',
    `fingerprint` VARCHAR(128) NULL DEFAULT '' COMMENT '去重指纹',
    `reason` TEXT NULL COMMENT '准入/排除原因与风险说明',
    `action_status` VARCHAR(128) NULL DEFAULT '' COMMENT '行动进度状态',
    `next_action` TEXT NULL COMMENT '下一步具体行动建议',
    `artifacts` JSON NULL COMMENT '关联交付件/简历附件列表',
    `first_seen_at` DATETIME NOT NULL COMMENT '首次发现时间',
    `last_verified_at` DATETIME NOT NULL COMMENT '最近核验时间',
    `last_run_id` VARCHAR(64) NULL DEFAULT '' COMMENT '最近关联运行批次ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '首次入库时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近更新时间',
    
    KEY `idx_platform` (`platform`),
    KEY `idx_status` (`status`),
    KEY `idx_priority` (`priority`),
    KEY `idx_score` (`score`),
    KEY `idx_last_verified` (`last_verified_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='兼职与远程赚钱机会明细表'
;

-- ----------------------------
-- Table structure for part_time_scan_runs
-- ----------------------------
CREATE TABLE IF NOT EXISTS `part_time_scan_runs` (
    `run_id` VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '运行批次ID(如 2026-08-07T2227+0800)',
    `summary` TEXT NULL COMMENT '本轮扫描核心结论',
    `total_opportunities` INT NOT NULL DEFAULT 0 COMMENT '维护的机会总数',
    `active_count` INT NOT NULL DEFAULT 0 COMMENT '活跃可行动数量',
    `watchlist_count` INT NOT NULL DEFAULT 0 COMMENT '观察队列数量',
    `excluded_count` INT NOT NULL DEFAULT 0 COMMENT '已排除数量',
    `report_path` VARCHAR(256) NOT NULL COMMENT 'Markdown报告相对路径',
    `started_at` DATETIME NOT NULL COMMENT '任务开始时间',
    `finished_at` DATETIME NULL COMMENT '任务结束时间',
    `duration_sec` FLOAT NOT NULL DEFAULT 0 COMMENT '耗时(秒)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='兼职与远程机会扫描批次日志表'
;

-- ----------------------------
-- Table structure for rule_sources
-- ----------------------------
CREATE TABLE `rule_sources` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `rule_id` bigint unsigned NOT NULL,
  `source_type` enum('manual','markdown','task','api') NOT NULL,
  `source_ref` varchar(1000) NOT NULL,
  `source_heading` varchar(500) DEFAULT NULL,
  `source_key` char(64) NOT NULL,
  `metadata` json NOT NULL,
  `imported_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uq_rule_source` (`rule_id`,`source_key`),
  KEY `idx_rule_sources_ref` (`source_type`,`source_key`),
  CONSTRAINT `fk_rule_source_rule` FOREIGN KEY (`rule_id`) REFERENCES `rules` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=443 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for rules
-- ----------------------------
CREATE TABLE `rules` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `title` varchar(240) NOT NULL,
  `summary` varchar(1000) DEFAULT NULL,
  `content` mediumtext NOT NULL,
  `category` enum('frontend','backend','fullstack','general') NOT NULL DEFAULT 'general',
  `group_name` varchar(80) NOT NULL DEFAULT '未分组',
  `priority` enum('low','medium','high','critical') NOT NULL DEFAULT 'medium',
  `content_hash` char(64) NOT NULL,
  `globs` json NOT NULL,
  `tags` json NOT NULL,
  `always_apply` tinyint(1) NOT NULL DEFAULT '0',
  `status` enum('active','disabled') NOT NULL DEFAULT 'active',
  `deleted_at` datetime(3) DEFAULT NULL,
  `deleted_by` varchar(120) DEFAULT NULL,
  `duplicate_count` int unsigned NOT NULL DEFAULT '0',
  `metadata` json NOT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uq_rules_content_hash` (`content_hash`),
  KEY `idx_rules_filter` (`status`,`category`,`priority`,`updated_at`),
  KEY `idx_rules_group` (`group_name`,`status`,`updated_at`),
  KEY `idx_rules_deleted` (`deleted_at`,`status`,`updated_at`)
) ENGINE=InnoDB AUTO_INCREMENT=279 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for schedule_runs
-- ----------------------------
CREATE TABLE `schedule_runs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `schedule_id` bigint unsigned NOT NULL,
  `task_id` bigint unsigned DEFAULT NULL,
  `scheduled_for` datetime(3) NOT NULL,
  `triggered_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `status` enum('created','skipped','failed') NOT NULL,
  `message` text,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uq_schedule_run` (`schedule_id`,`scheduled_for`),
  KEY `idx_runs_schedule` (`schedule_id`,`triggered_at`),
  KEY `fk_run_task` (`task_id`),
  CONSTRAINT `fk_run_schedule` FOREIGN KEY (`schedule_id`) REFERENCES `task_schedules` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_run_task` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for schema_migrations
-- ----------------------------
CREATE TABLE IF NOT EXISTS schema_migrations (
        id VARCHAR(80) PRIMARY KEY,
        applied_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
      ) ENGINE=InnoDB
;

-- ----------------------------
-- Table structure for self_project_iterations
-- ----------------------------
CREATE TABLE IF NOT EXISTS self_project_iterations (
      id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      repo_name VARCHAR(128) NOT NULL,
      repo_owner VARCHAR(64) NOT NULL DEFAULT 'loulanyue',
      current_stars INT UNSIGNED DEFAULT 0,
      iteration_theme VARCHAR(256) NOT NULL,
      category VARCHAR(64) NOT NULL,
      action_type VARCHAR(64) NOT NULL,
      details TEXT,
      readiness_score INT UNSIGNED DEFAULT 0,
      log_file VARCHAR(256),
      commit_hash VARCHAR(64),
      run_time DATETIME NOT NULL,
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      INDEX idx_repo (repo_owner, repo_name),
      INDEX idx_category (category),
      INDEX idx_run_time (run_time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
;

-- ----------------------------
-- Table structure for soft_exam_knowledge_points
-- ----------------------------
CREATE TABLE IF NOT EXISTS `soft_exam_knowledge_points` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `business_category` VARCHAR(150) NOT NULL COMMENT '业务数据分类 (通常取自图片主名称，如第一章.png对应第一章)',
    `source_image` VARCHAR(255) NOT NULL COMMENT '所属来源图片名称/文件名',
    `chapter` VARCHAR(100) NOT NULL COMMENT '主章节分类 (如: 软件开发方法、软件工程基础等)',
    `category` VARCHAR(150) NOT NULL COMMENT '分类/模块层级 (如: 净室软件工程、敏捷方法、UML建模等)',
    `knowledge_point` VARCHAR(255) NOT NULL COMMENT '知识点核心名称',
    `mnemonic_point` TEXT NULL COMMENT '改编易记知识点 (口诀、速记联想、高频精简记忆词)',
    `recommended_stars` TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '推荐星级 (1~5星，对应导图中的星标数量)',
    `parent_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '父级考点ID (支持无限级树形层级)',
    `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序权重',
    `notes` TEXT NULL COMMENT '考点详细解析/考试年份频次备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    INDEX `idx_business_category` (`business_category`),
    INDEX `idx_source_image` (`source_image`),
    INDEX `idx_chapter_category` (`chapter`, `category`),
    INDEX `idx_stars` (`recommended_stars`),
    INDEX `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='软考核心考点速记表'
;

-- ----------------------------
-- Table structure for task_artifacts
-- ----------------------------
CREATE TABLE `task_artifacts` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `task_id` bigint unsigned NOT NULL,
  `attempt_id` bigint unsigned DEFAULT NULL,
  `artifact_type` varchar(40) NOT NULL,
  `name` varchar(200) NOT NULL,
  `location` text NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `fk_artifact_task` (`task_id`),
  KEY `fk_artifact_attempt` (`attempt_id`),
  CONSTRAINT `fk_artifact_attempt` FOREIGN KEY (`attempt_id`) REFERENCES `task_attempts` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_artifact_task` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for task_attempts
-- ----------------------------
CREATE TABLE `task_attempts` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `task_id` bigint unsigned NOT NULL,
  `agent_id` bigint unsigned DEFAULT NULL,
  `agent_public_id` varchar(40) NOT NULL,
  `attempt_no` int unsigned NOT NULL,
  `status` enum('claimed','running','blocked','completed','failed','expired') NOT NULL DEFAULT 'claimed',
  `claimed_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `started_at` datetime(3) DEFAULT NULL,
  `heartbeat_at` datetime(3) DEFAULT NULL,
  `lease_expires_at` datetime(3) NOT NULL,
  `finished_at` datetime(3) DEFAULT NULL,
  `progress_percent` tinyint unsigned NOT NULL DEFAULT '0',
  `summary` text,
  `result` json DEFAULT NULL,
  `error_message` text,
  `metadata` json NOT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uq_task_attempt` (`task_id`,`attempt_no`),
  KEY `idx_attempt_lease` (`status`,`lease_expires_at`),
  KEY `idx_attempt_agent` (`agent_public_id`,`status`),
  KEY `fk_attempt_agent` (`agent_id`),
  CONSTRAINT `fk_attempt_agent` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_attempt_task` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for task_dependencies
-- ----------------------------
CREATE TABLE `task_dependencies` (
  `task_id` bigint unsigned NOT NULL,
  `depends_on_task_id` bigint unsigned NOT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`task_id`,`depends_on_task_id`),
  KEY `fk_dependency_parent` (`depends_on_task_id`),
  CONSTRAINT `fk_dependency_parent` FOREIGN KEY (`depends_on_task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_dependency_task` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for task_events
-- ----------------------------
CREATE TABLE `task_events` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `task_id` bigint unsigned NOT NULL,
  `attempt_id` bigint unsigned DEFAULT NULL,
  `event_type` varchar(80) NOT NULL,
  `actor_type` enum('user','agent','scheduler','system') NOT NULL,
  `actor_id` varchar(80) DEFAULT NULL,
  `from_status` varchar(40) DEFAULT NULL,
  `to_status` varchar(40) DEFAULT NULL,
  `payload` json NOT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `idx_events_task` (`task_id`,`created_at`),
  KEY `fk_event_attempt` (`attempt_id`),
  CONSTRAINT `fk_event_attempt` FOREIGN KEY (`attempt_id`) REFERENCES `task_attempts` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_event_task` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=430 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for task_notes
-- ----------------------------
CREATE TABLE `task_notes` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `task_id` bigint unsigned NOT NULL,
  `attempt_id` bigint unsigned DEFAULT NULL,
  `author_type` enum('user','agent','system') NOT NULL,
  `author_id` varchar(80) DEFAULT NULL,
  `body` text NOT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `idx_notes_task` (`task_id`,`created_at`),
  KEY `fk_note_attempt` (`attempt_id`),
  CONSTRAINT `fk_note_attempt` FOREIGN KEY (`attempt_id`) REFERENCES `task_attempts` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_note_task` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for task_rules
-- ----------------------------
CREATE TABLE `task_rules` (
  `task_id` bigint unsigned NOT NULL,
  `rule_id` bigint unsigned NOT NULL,
  `relation_type` enum('derived','linked') NOT NULL DEFAULT 'derived',
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`task_id`,`rule_id`),
  KEY `idx_task_rules_rule` (`rule_id`,`task_id`),
  CONSTRAINT `fk_task_rule_rule` FOREIGN KEY (`rule_id`) REFERENCES `rules` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_task_rule_task` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for task_schedules
-- ----------------------------
CREATE TABLE `task_schedules` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `name` varchar(160) NOT NULL,
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `schedule_type` enum('once','interval','cron') NOT NULL,
  `run_at` datetime(3) DEFAULT NULL,
  `interval_seconds` int unsigned DEFAULT NULL,
  `cron_expression` varchar(120) DEFAULT NULL,
  `timezone` varchar(80) NOT NULL DEFAULT 'Asia/Shanghai',
  `task_template` json NOT NULL,
  `misfire_policy` enum('skip','fire_once','catch_up') NOT NULL DEFAULT 'fire_once',
  `overlap_policy` enum('forbid','allow','replace') NOT NULL DEFAULT 'forbid',
  `max_catch_up` int unsigned NOT NULL DEFAULT '1',
  `next_run_at` datetime(3) DEFAULT NULL,
  `last_run_at` datetime(3) DEFAULT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `idx_schedules_due` (`enabled`,`next_run_at`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for tasks
-- ----------------------------
CREATE TABLE `tasks` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `public_id` varchar(40) NOT NULL,
  `external_id` varchar(190) DEFAULT NULL,
  `title` varchar(240) NOT NULL,
  `objective` text NOT NULL,
  `normative_constraint` text,
  `instructions` json NOT NULL,
  `acceptance_criteria` json NOT NULL,
  `context` json NOT NULL,
  `execution` json NOT NULL,
  `metadata` json NOT NULL,
  `priority` enum('low','medium','high','critical') NOT NULL DEFAULT 'medium',
  `status` enum('pending','claimed','running','blocked','review','completed','failed','cancelled') NOT NULL DEFAULT 'pending',
  `source_type` enum('manual','api','agent','schedule','webhook') NOT NULL DEFAULT 'manual',
  `source_id` varchar(190) DEFAULT NULL,
  `schedule_id` bigint unsigned DEFAULT NULL,
  `current_attempt_id` bigint unsigned DEFAULT NULL,
  `claimed_by` varchar(40) DEFAULT NULL,
  `lease_expires_at` datetime(3) DEFAULT NULL,
  `attempt_count` int unsigned NOT NULL DEFAULT '0',
  `version` int unsigned NOT NULL DEFAULT '1',
  `due_at` datetime(3) DEFAULT NULL,
  `completed_at` datetime(3) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `deleted_by` varchar(120) DEFAULT NULL,
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uq_tasks_external` (`source_type`,`external_id`),
  KEY `idx_tasks_queue` (`status`,`priority`,`created_at`),
  KEY `idx_tasks_agent` (`claimed_by`,`status`),
  KEY `idx_tasks_schedule` (`schedule_id`,`status`),
  KEY `idx_tasks_deleted` (`deleted_at`,`status`,`updated_at`),
  CONSTRAINT `fk_tasks_schedule` FOREIGN KEY (`schedule_id`) REFERENCES `task_schedules` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=122 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
;

-- ----------------------------
-- Table structure for agent_architecture_positions
-- ----------------------------
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

-- ----------------------------
-- Table structure for agent_architecture_requirements
-- ----------------------------
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

SET FOREIGN_KEY_CHECKS = 1;

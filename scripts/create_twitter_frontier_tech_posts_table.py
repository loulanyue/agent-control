import pymysql

conn = pymysql.connect(host='127.0.0.1', port=13306, user='root', password='', database='agent_control')
cursor = conn.cursor()

create_sql = """
CREATE TABLE IF NOT EXISTS `twitter_frontier_tech_posts` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `tweet_id` VARCHAR(64) NOT NULL UNIQUE COMMENT '推文唯一ID',
  `author_username` VARCHAR(64) NOT NULL DEFAULT 'trq212' COMMENT '作者handle',
  `author_name` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '作者昵称',
  `content` TEXT COMMENT '推文正文',
  `content_zh` TEXT COMMENT '推文内容中文',
  `tweet_url` VARCHAR(512) NOT NULL COMMENT '推文链接',
  `published_at` DATETIME NULL COMMENT '推文原始发布时间',
  `media_urls` JSON NULL COMMENT '媒体附件列表(图片/视频等)',
  `metrics` JSON NULL COMMENT '互动数据(点赞/转推/回复等)',
  `is_retweet` TINYINT(1) DEFAULT 0 COMMENT '是否转推/引用',
  `raw_data` JSON NULL COMMENT '原始推文JSON数据',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_author` (`author_username`),
  INDEX `idx_published_at` (`published_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

cursor.execute(create_sql)
conn.commit()
cursor.execute('SHOW TABLES LIKE "%frontier%";')
print("Matched tables:", cursor.fetchall())
cursor.execute('DESCRIBE `twitter_frontier_tech_posts`;')
for col in cursor.fetchall():
    print(col)

conn.close()

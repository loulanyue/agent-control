import pymysql

conn = pymysql.connect(host='127.0.0.1', port=13306, user='root', password='', database='agent_control')
cursor = conn.cursor()

try:
    cursor.execute("""
    ALTER TABLE twitter_frontier_tech_posts
    ADD COLUMN content_zh TEXT NULL COMMENT '推文内容中文'
    AFTER content;
    """)
    conn.commit()
    print("Successfully added content_zh column to twitter_frontier_tech_posts!")
except Exception as e:
    print("Alter table note:", e)

cursor.execute("DESCRIBE twitter_frontier_tech_posts;")
for col in cursor.fetchall():
    print(col)

conn.close()

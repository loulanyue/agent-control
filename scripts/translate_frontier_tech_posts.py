import time
import re
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import translators as ts
from db.session import SessionLocal
from app.models.extensions import TwitterFrontierTechPost

def translate_content(text: str) -> str:
    if not text or not text.strip():
        return ""
    clean = text.strip()
    
    # Try bing first, fallback to alibaba, then baidu
    for eng in ['bing', 'alibaba', 'baidu']:
        try:
            res = ts.translate_text(clean, translator=eng, from_language='en', to_language='zh')
            if res and has_chinese(res):
                return str(res).strip()
        except Exception:
            continue
    return ""

def has_chinese(text: str) -> bool:
    if not text:
        return False
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def main():
    db = SessionLocal()
    posts = db.query(TwitterFrontierTechPost).all()
    
    needing = [p for p in posts if not has_chinese(p.content_zh)]
    total = len(needing)
    print(f"Total posts in DB: {len(posts)}. Still needing Chinese translation: {total}.")
    
    if total == 0:
        db.close()
        print("All posts already have Chinese translation!")
        return

    tasks = [(p.id, p.content) for p in needing]
    db.close()

    completed = 0
    batch = []
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_map = {executor.submit(translate_content, cnt): pid for pid, cnt in tasks}
        for future in as_completed(future_map):
            pid = future_map[future]
            try:
                zh = future.result()
                if zh and has_chinese(zh):
                    batch.append((pid, zh))
            except Exception as e:
                print(f"Error translating post {pid}: {e}")
                
            completed += 1
            if completed % 10 == 0 or completed == total:
                print(f"Progress: {completed}/{total} ({completed/total*100:.1f}%) processed...")
                
            if len(batch) >= 10:
                db_write = SessionLocal()
                for uid, uzh in batch:
                    db_write.query(TwitterFrontierTechPost).filter(TwitterFrontierTechPost.id == uid).update(
                        {"content_zh": uzh}
                    )
                db_write.commit()
                db_write.close()
                batch = []

    if batch:
        db_write = SessionLocal()
        for uid, uzh in batch:
            db_write.query(TwitterFrontierTechPost).filter(TwitterFrontierTechPost.id == uid).update(
                {"content_zh": uzh}
            )
        db_write.commit()
        db_write.close()

    # Re-verify
    db = SessionLocal()
    all_posts = db.query(TwitterFrontierTechPost).all()
    actual_chinese = sum(1 for p in all_posts if has_chinese(p.content_zh))
    db.close()
    print(f"\nCompleted! Total posts: {len(all_posts)}, With real Chinese content: {actual_chinese}/{len(all_posts)} ({actual_chinese/len(all_posts)*100:.1f}%).")

if __name__ == "__main__":
    main()

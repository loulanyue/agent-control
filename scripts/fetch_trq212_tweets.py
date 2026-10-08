import subprocess
import time
import re
import json
import requests
from datetime import datetime
from db.session import SessionLocal
from app.models.extensions import TwitterFrontierTechPost

def run_osascript(script: str) -> str:
    res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return res.stdout.strip()

def activate_and_scroll():
    script = """
    tell application "Google Chrome"
        repeat with w in windows
            set i to 0
            repeat with t in tabs of w
                set i to i + 1
                if URL of t contains "x.com/trq212" then
                    set active tab index of w to i
                    set index of w to 1
                    activate
                    exit repeat
                end if
            end repeat
        end repeat
    end tell
    delay 0.3
    tell application "System Events"
        tell process "Google Chrome"
            key code 121 -- Page Down
            delay 0.4
            key code 121 -- Page Down
            delay 0.4
            keystroke "a" using {command down}
            delay 0.2
            keystroke "c" using {command down}
        end tell
    end tell
    """
    run_osascript(script)

def get_clipboard() -> str:
    res = subprocess.run(["pbpaste"], capture_output=True, text=True)
    return res.stdout

def parse_text_blocks(raw_text: str):
    """
    Parses text blocks copied from X timeline.
    Tweets usually have:
    Thariq
    @trq212
    ·
    <Date/Time>
    <Content text...>
    <Metrics / Replies / Reposts / Likes>
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    posts = []
    
    i = 0
    while i < len(lines):
        # Match Thariq / @trq212 pattern
        if lines[i] == "@trq212" or (i + 1 < len(lines) and lines[i+1] == "@trq212"):
            if lines[i] == "@trq212":
                author_name = lines[i-1] if i > 0 else "Thariq"
                author_user = "trq212"
                curr = i + 1
            else:
                author_name = lines[i]
                author_user = "trq212"
                curr = i + 2
            
            # Next line might be "·"
            if curr < len(lines) and lines[curr] == "·":
                curr += 1
            
            # Next line is date/relative time (e.g. "19h", "Oct 2", "Mar 21", "2024年1月2日")
            pub_date_str = ""
            if curr < len(lines):
                pub_date_str = lines[curr]
                curr += 1
            
            # Collect content until next tweet header, "Who to follow", "Trending", or footer
            content_lines = []
            while curr < len(lines):
                l = lines[curr]
                if l in ["@trq212", "Thariq", "Who to follow", "Trending now", "What’s happening", "Terms", "© 2026 X Corp."]:
                    break
                if curr + 1 < len(lines) and lines[curr+1] == "@trq212":
                    break
                # Skip pure UI noise
                if l in ["Quote", "Pinned", "Show more", "Follow", "Following"]:
                    curr += 1
                    continue
                content_lines.append(l)
                curr += 1
            
            content = "\n".join(content_lines)
            if content and len(content) > 5:
                # Generate a deterministic tweet_id hash if exact id isn't in plaintext
                import hashlib
                content_hash = hashlib.md5((content + pub_date_str).encode('utf-8')).hexdigest()
                posts.append({
                    "tweet_id": f"trq212_{content_hash[:16]}",
                    "author_username": author_user,
                    "author_name": author_name,
                    "content": content,
                    "pub_date_str": pub_date_str,
                    "tweet_url": f"https://x.com/trq212"
                })
            i = curr
        else:
            i += 1
    return posts

def main():
    print("Starting continuous scrape of https://x.com/trq212 via Chrome session...")
    db = SessionLocal()
    total_saved = 0
    seen_ids = set()
    
    # Query already stored tweet_ids
    existing_records = db.query(TwitterFrontierTechPost.tweet_id).all()
    for (tid,) in existing_records:
        seen_ids.add(tid)
        
    print(f"Loaded {len(seen_ids)} existing tweet IDs from database.")
    
    # Loop scroll iterations
    rounds = 35
    for r in range(1, rounds + 1):
        activate_and_scroll()
        time.sleep(0.8)
        raw_text = get_clipboard()
        posts = parse_text_blocks(raw_text)
        
        batch_new = 0
        for p in posts:
            if p["tweet_id"] not in seen_ids:
                seen_ids.add(p["tweet_id"])
                new_post = TwitterFrontierTechPost(
                    tweet_id=p["tweet_id"],
                    author_username=p["author_username"],
                    author_name=p["author_name"],
                    content=p["content"],
                    tweet_url=p["tweet_url"],
                    published_at=datetime.utcnow(),
                    media_urls=[],
                    metrics={"raw_date": p["pub_date_str"]},
                    is_retweet=0,
                    raw_data={"pub_date_str": p["pub_date_str"], "raw_content": p["content"]}
                )
                db.add(new_post)
                batch_new += 1
                total_saved += 1
        
        if batch_new > 0:
            db.commit()
            print(f"Round {r}/{rounds}: scraped {len(posts)} posts in viewport, saved {batch_new} NEW posts. (Total DB: {len(seen_ids)})")
        else:
            print(f"Round {r}/{rounds}: scraped {len(posts)} posts in viewport, 0 new.")
            
    db.close()
    print(f"\nFinished scraping! Total new posts inserted: {total_saved}. Grand total: {len(seen_ids)}.")

if __name__ == "__main__":
    main()

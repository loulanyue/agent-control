#!/usr/bin/env python3
"""
Sync GitHub Pull Requests Lifecycle & Contributions Status for loulanyue.
"""
import sys
import os
import json
import re
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import SessionLocal
from app.models.extensions import GithubPrLifecycle, GithubContribution

import shutil

# Ensure standard binary search paths are available in environment
for extra_p in ["/opt/homebrew/bin", "/usr/local/bin", os.path.expanduser("~/.local/bin")]:
    if extra_p not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{extra_p}:{os.environ.get('PATH', '')}"

def get_gh_bin() -> str:
    found = shutil.which("gh")
    if found:
        return found
    for fallback in ["/opt/homebrew/bin/gh", "/usr/local/bin/gh", "/usr/bin/gh"]:
        if os.path.isfile(fallback) and os.access(fallback, os.X_OK):
            return fallback
    return "gh"

def parse_iso_dt(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str or dt_str.startswith("0001-01-01"):
        return None
    try:
        # e.g. "2026-09-04T09:08:43Z"
        clean_str = dt_str.rstrip("Z")
        return datetime.fromisoformat(clean_str)
    except Exception:
        return None

def normalize_pr_url(url: Optional[str]) -> str:
    if not url:
        return ""
    # Strip asterisks / markdown formatting
    u = url.strip().rstrip("*").strip()
    # Strip issue comments / anchors
    u = u.split("#")[0].strip()
    return u

def extract_pr_urls(text: Optional[str]):
    if not text:
        return []
    # Match github pull urls
    matches = re.findall(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/pull/\d+", text)
    return matches

def sync_github_prs_data():
    gh_bin = get_gh_bin()
    print(f"Fetching PRs from GitHub CLI (bin: {gh_bin}, author: loulanyue)...")
    cmd = [
        gh_bin, "search", "prs",
        "--author", "loulanyue",
        "--limit", "600",
        "--json", "number,repository,state,title,url,createdAt,updatedAt,closedAt"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
    if res.returncode != 0:
        raise RuntimeError(f"gh search failed: {res.stderr}")
    
    items = json.loads(res.stdout)
    print(f"Successfully fetched {len(items)} PRs from GitHub.")
    
    gh_map: Dict[str, Any] = {}
    self_pr_count = 0
    for item in items:
        repo_info = item.get("repository", {})
        name_with_owner = repo_info.get("nameWithOwner", "")
        owner = name_with_owner.split("/")[0].lower() if "/" in name_with_owner else ""
        url = item.get("url", "")
        # 严格剔除自身项目的 PR (如 loulanyue/interview-notes, loulanyue/spec-kit-zh 等)
        if owner == "loulanyue" or url.startswith("https://github.com/loulanyue/"):
            self_pr_count += 1
            continue
        gh_map[url] = item

    print(f"Total fetched: {len(items)}, Filtered out self-owned: {self_pr_count}, External PRs: {len(gh_map)}")

    db = SessionLocal()
    try:
        now = datetime.utcnow()
        # 彻底清理数据库中属于自身项目的 PR 与开源贡献记录
        deleted_prs = db.query(GithubPrLifecycle).filter(
            (GithubPrLifecycle.repo_owner == "loulanyue") | (GithubPrLifecycle.pr_url.like("https://github.com/loulanyue/%"))
        ).delete(synchronize_session=False)

        deleted_contribs = db.query(GithubContribution).filter(
            (GithubContribution.repo_owner == "loulanyue") | (GithubContribution.pr_url.like("https://github.com/loulanyue/%"))
        ).delete(synchronize_session=False)
        if deleted_prs or deleted_contribs:
            print(f"Purged self-owned records from DB: {deleted_prs} PRs, {deleted_contribs} contributions.")

        updated_lifecycle_count = 0
        inserted_lifecycle_count = 0
        updated_contrib_count = 0
        
        # 1. Update / Insert GithubPrLifecycle (仅外部项目)
        db_prs = db.query(GithubPrLifecycle).all()
        existing_prs_by_url = {p.pr_url: p for p in db_prs}
        
        for url, item in gh_map.items():
            st = item.get("state", "").upper() # OPEN, CLOSED, MERGED
            created_dt = parse_iso_dt(item.get("createdAt"))
            updated_dt = parse_iso_dt(item.get("updatedAt"))
            closed_dt = parse_iso_dt(item.get("closedAt"))
            merged_dt = closed_dt if st == "MERGED" else None
            
            if url in existing_prs_by_url:
                p = existing_prs_by_url[url]
                changed = False
                if p.state != st:
                    p.state = st
                    changed = True
                if p.title != item.get("title", p.title):
                    p.title = item.get("title", p.title)
                    changed = True
                if updated_dt and p.updated_at != updated_dt:
                    p.updated_at = updated_dt
                    changed = True
                if closed_dt and p.closed_at != closed_dt:
                    p.closed_at = closed_dt
                    changed = True
                if merged_dt and p.merged_at != merged_dt:
                    p.merged_at = merged_dt
                    changed = True
                
                p.last_sync_time = now
                if changed:
                    updated_lifecycle_count += 1
            else:
                repo_owner = ""
                repo_name = ""
                if "repository" in item:
                    repo_name = item["repository"].get("name", "")
                    name_with_owner = item["repository"].get("nameWithOwner", "")
                    if "/" in name_with_owner:
                        repo_owner = name_with_owner.split("/")[0]
                    else:
                        repo_owner = "loulanyue"
                
                new_pr = GithubPrLifecycle(
                    repo_name=repo_name,
                    repo_owner=repo_owner,
                    pr_number=item.get("number", 0),
                    title=item.get("title", ""),
                    state=st,
                    created_at=created_dt,
                    updated_at=updated_dt,
                    closed_at=closed_dt,
                    merged_at=merged_dt,
                    pr_url=url,
                    branch_name="",
                    mergeable_status="UNKNOWN",
                    review_decision="NONE",
                    category="upstream",
                    last_sync_time=now
                )
                db.add(new_pr)
                inserted_lifecycle_count += 1
        
        db.flush()
        
        # 2. Update GithubContribution
        contribs = db.query(GithubContribution).all()
        for c in contribs:
            urls = extract_pr_urls(c.pr_url)
            gh_item = None
            for u in urls:
                if u in gh_map:
                    gh_item = gh_map[u]
                    break
            
            # If not in gh_map and it's a specific single PR (e.g. facebook/react)
            if not gh_item and urls and len(urls) == 1:
                single_url = urls[0]
                # Try gh pr view
                try:
                    p_res = subprocess.run(
                        [gh_bin, "pr", "view", single_url, "--json", "state,closedAt,mergedAt"],
                        capture_output=True, text=True, timeout=10, env=os.environ
                    )
                    if p_res.returncode == 0:
                        single_data = json.loads(p_res.stdout)
                        gh_item = {
                            "state": single_data.get("state", "").upper(),
                            "closedAt": single_data.get("closedAt"),
                            "mergedAt": single_data.get("mergedAt")
                        }
                except Exception as ex:
                    pass
            
            if gh_item:
                target_state = gh_item.get("state", "").upper()
                c_changed = False
                if c.status != target_state:
                    c.status = target_state
                    c_changed = True
                
                if target_state == "MERGED":
                    merged_iso = gh_item.get("mergedAt") or gh_item.get("closedAt")
                    m_dt = parse_iso_dt(merged_iso)
                    if m_dt and c.merged_at != m_dt:
                        c.merged_at = m_dt
                        c_changed = True
                
                if c_changed:
                    c.updated_at = now
                    updated_contrib_count += 1

        db.commit()
        print("Sync completed successfully!")
        print(f"Total PRs processed from GitHub: {len(items)}")
        print(f"GithubPrLifecycle updated: {updated_lifecycle_count}, inserted: {inserted_lifecycle_count}")
        print(f"GithubContribution updated: {updated_contrib_count}")
        return {
            "total_fetched": len(items),
            "external_prs": len(gh_map),
            "purged_self_prs": deleted_prs,
            "purged_self_contribs": deleted_contribs,
            "updated_lifecycle": updated_lifecycle_count,
            "inserted_lifecycle": inserted_lifecycle_count,
            "updated_contributions": updated_contrib_count
        }
    except Exception as e:
        db.rollback()
        print(f"Error during sync: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    sync_github_prs_data()

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

ENDPOINTS = [
    ("/api/v1/dashboard/stats", False),
    ("/api/v1/extensions/talent-notices?page=1&page_size=5", True),
    ("/api/v1/extensions/notice-crawl-runs?page=1&page_size=5", True),
    ("/api/v1/extensions/github-contributions?page=1&page_size=5", True),
    ("/api/v1/extensions/github-prs?page=1&page_size=5", True),
    ("/api/v1/extensions/job-positions?page=1&page_size=5", True),
    ("/api/v1/extensions/job-requirements?page=1&page_size=5", True),
    ("/api/v1/extensions/part-time-opportunities?page=1&page_size=5", True),
    ("/api/v1/extensions/part-time-scan-runs?page=1&page_size=5", True),
    ("/api/v1/extensions/soft-exam?page=1&page_size=5", True),
    ("/api/v1/extensions/self-project-iterations?page=1&page_size=5", True),
    ("/api/v1/extensions/bitcoin-mining-runs?page=1&page_size=5", True),
    ("/api/v1/tasks?page=1&page_size=5", True),
    ("/api/v1/tasks/attempts?page=1&page_size=5", True),
    ("/api/v1/tasks/artifacts?page=1&page_size=5", True),
    ("/api/v1/tasks/notes?page=1&page_size=5", True),
    ("/api/v1/agents?page=1&page_size=5", True),
    ("/api/v1/agents/api-clients?page=1&page_size=5", True),
    ("/api/v1/rules?page=1&page_size=5", True),
    ("/api/v1/rules/sources?page=1&page_size=5", True),
    ("/api/v1/graphs?page=1&page_size=5", True),
    ("/api/v1/graphs/runs?page=1&page_size=5", True),
    ("/api/v1/schedules?page=1&page_size=5", True),
    ("/api/v1/schedules/runs?page=1&page_size=5", True),
]

def test_all_apis():
    print("==================================================")
    print("Testing All Pagination APIs & Dashboard Stats...")
    print("==================================================")
    all_passed = True
    for url, is_paginated in ENDPOINTS:
        try:
            resp = client.get(url)
            if resp.status_code != 200:
                print(f"[FAIL] {url} -> Status {resp.status_code}: {resp.text}")
                all_passed = False
                continue
            data = resp.json()
            if is_paginated:
                assert "items" in data, f"Missing 'items' in response for {url}"
                assert "total" in data, f"Missing 'total' in response for {url}"
                assert "page" in data, f"Missing 'page' in response for {url}"
                assert "page_size" in data, f"Missing 'page_size' in response for {url}"
                assert "total_pages" in data, f"Missing 'total_pages' in response for {url}"
                print(f"[OK] {url.split('?')[0]:<45} | total={data['total']}, items={len(data['items'])}, pages={data['total_pages']}")
            else:
                print(f"[OK] {url:<45} | stats count={len(data)}")
        except Exception as e:
            print(f"[ERROR] {url} -> Exception: {e}")
            all_passed = False

    # Test Dashboard HTML UI
    print("--------------------------------------------------")
    resp_dashboard = client.get("/dashboard")
    assert resp_dashboard.status_code == 200
    assert "Agent Control 业务数据多维控制台" in resp_dashboard.text
    print(f"[OK] GET /dashboard                           | HTML rendered successfully ({len(resp_dashboard.text)} bytes)")

    # Also test search filtering on a sample endpoint
    print("--------------------------------------------------")
    search_url = "/api/v1/extensions/github-contributions?page=1&page_size=5&keyword=fix"
    resp_search = client.get(search_url)
    assert resp_search.status_code == 200
    search_data = resp_search.json()
    assert "items" in search_data
    print(f"[OK] Search query ({search_url}) -> matched total={search_data['total']}")

    # Test talent notices independent filters: date and category
    print("--------------------------------------------------")
    resp_date = client.get("/api/v1/extensions/talent-notices?publish_date=2026-09-09&page_size=5")
    assert resp_date.status_code == 200
    d_date = resp_date.json()
    assert d_date["total"] == 83
    print(f"[OK] Talent Notice by Date (2026-09-09) -> matched total={d_date['total']}")

    resp_cat = client.get("/api/v1/extensions/talent-notices?category=E类&page_size=5")
    assert resp_cat.status_code == 200
    d_cat = resp_cat.json()
    assert d_cat["total"] >= 1361
    print(f"[OK] Talent Notice by Category (E类) -> matched total={d_cat['total']}")

    resp_combo = client.get("/api/v1/extensions/talent-notices?publish_date=2026-09-09&category=E类&page_size=5")
    assert resp_combo.status_code == 200
    d_combo = resp_combo.json()
    assert d_combo["total"] == 72
    print(f"[OK] Talent Notice Combo (Date 2026-09-09 + Category E类) -> matched total={d_combo['total']}")

    print("==================================================")
    if all_passed:
        print("🎉 ALL 24 BUSINESS PAGINATION ENDPOINTS & DASHBOARD PASSED PERFECTLY!")
    else:
        print("❌ SOME ENDPOINTS FAILED")
    print("==================================================")
    return all_passed

if __name__ == "__main__":
    success = test_all_apis()
    if not success:
        sys.exit(1)

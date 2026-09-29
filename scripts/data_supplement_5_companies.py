# -*- coding: utf-8 -*-
"""
5 家半导体公司精准补充岗位数据集 (合计 291 岗):
1. 杰华特微电子股份有限公司: 112 岗 (总目标 142 岗)
2. 杭州芯云半导体集团有限公司: 36 岗 (总目标 64 岗)
3. 杭州行芯科技有限公司: 18 岗 (总目标 46 岗)
4. 浙江地芯引力科技有限公司: 6 岗 (总目标 31 岗)
5. 杭州国科微电子有限公司: 119 岗 (总目标 144 岗)
"""

import os
import sys

# Ensure current script directory and parent directory are on sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
for p in [_current_dir, _parent_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from data_supp_jwh import get_jwh_jobs
    from data_supp_xinyun import get_xinyun_jobs
    from data_supp_xingxin import get_xingxin_jobs
    from data_supp_dixin import get_dixin_jobs
    from data_supp_guoke import get_guoke_jobs
except ImportError:
    from scripts.data_supp_jwh import get_jwh_jobs
    from scripts.data_supp_xinyun import get_xinyun_jobs
    from scripts.data_supp_xingxin import get_xingxin_jobs
    from scripts.data_supp_dixin import get_dixin_jobs
    from scripts.data_supp_guoke import get_guoke_jobs

def get_all_supplement_jobs():
    jobs = []
    jwh = get_jwh_jobs()
    xinyun = get_xinyun_jobs()
    xingxin = get_xingxin_jobs()
    dixin = get_dixin_jobs()
    guoke = get_guoke_jobs()

    jobs.extend(jwh)
    jobs.extend(xinyun)
    jobs.extend(xingxin)
    jobs.extend(dixin)
    jobs.extend(guoke)

    return jobs

SUPPLEMENT_5_COMPANIES_JOBS = get_all_supplement_jobs()

if __name__ == "__main__":
    jobs = SUPPLEMENT_5_COMPANIES_JOBS
    print(f"Total supplement jobs loaded: {len(jobs)}")
    by_comp = {}
    for j in jobs:
        c = j["company_name"]
        by_comp[c] = by_comp.get(c, 0) + 1
    for c, cnt in by_comp.items():
        print(f" - {c}: {cnt}")

#!/bin/bash
# ==============================================================================
# 每天定时执行杭州人才数据全量抓取脚本 (09:00, 11:30, 17:25)
# 覆盖最近 3 天约 240 条数据并自动去重落库
# ==============================================================================

PROJECT_ROOT="/Users/youfanyu/Desktop/workspace/tpm"
LOG_DIR="${PROJECT_ROOT}/agent_control/logs"
mkdir -p "${LOG_DIR}"

LOG_FILE="${LOG_DIR}/talent_crawler_$(date +'%Y%m%d').log"

echo "========================================================" >> "${LOG_FILE}"
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting scheduled talent crawl ($(date +'%H:%M'))..." >> "${LOG_FILE}"

cd "${PROJECT_ROOT}" || exit 1

# 优先使用 agent_control 项目虚拟环境的 python3 (包含 sqlalchemy, requests 等完整依赖)
if [ -f "${PROJECT_ROOT}/agent_control/venv/bin/python3" ]; then
    PYTHON_BIN="${PROJECT_ROOT}/agent_control/venv/bin/python3"
else
    PYTHON_BIN="python3"
fi

${PYTHON_BIN} .agents/skills/hz-talent-crawler/scripts/crawler.py --days 3 --per-day 80 >> "${LOG_FILE}" 2>&1
EXIT_CODE=$?

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Scheduled talent crawl completed successfully." >> "${LOG_FILE}"
else
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Scheduled talent crawl failed with exit code ${EXIT_CODE}." >> "${LOG_FILE}"
fi
echo "========================================================" >> "${LOG_FILE}"

exit ${EXIT_CODE}


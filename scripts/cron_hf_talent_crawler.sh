#!/bin/bash
# ==============================================================================
# 每天定时执行合肥高层次人才数据全量抓取脚本 (11:25, 17:00)
# 覆盖合肥官方公示与结果最新数据，自动去脱敏与落库
# ==============================================================================

PROJECT_ROOT="/Users/youfanyu/Desktop/workspace/tpm"
LOG_DIR="${PROJECT_ROOT}/agent_control/logs"
mkdir -p "${LOG_DIR}"

LOG_FILE="${LOG_DIR}/hf_talent_crawler_$(date +'%Y%m%d').log"

echo "========================================================" >> "${LOG_FILE}"
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting scheduled Hefei talent crawl ($(date +'%H:%M'))..." >> "${LOG_FILE}"

cd "${PROJECT_ROOT}" || exit 1

if [ -f "${PROJECT_ROOT}/agent_control/venv/bin/python3" ]; then
    PYTHON_BIN="${PROJECT_ROOT}/agent_control/venv/bin/python3"
else
    PYTHON_BIN="python3"
fi

${PYTHON_BIN} .agents/skills/hf-talent-crawler/scripts/crawler.py --type publicity >> "${LOG_FILE}" 2>&1
EXIT_CODE=$?

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Scheduled Hefei talent crawl completed successfully." >> "${LOG_FILE}"
else
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Scheduled Hefei talent crawl failed with exit code ${EXIT_CODE}." >> "${LOG_FILE}"
fi
echo "========================================================" >> "${LOG_FILE}"

exit ${EXIT_CODE}

#!/usr/bin/env bash
# ==============================================================================
# Agent Control Plane - 一键启动与进程管理脚本
#
# 用法:
#   ./start.sh          # 默认以开发模式在前台运行 (含热重载，方便调试)
#   ./start.sh start    # 后台守护进程模式运行 (日志输出至 logs/agent_control.log)
#   ./start.sh stop     # 停止运行中的服务
#   ./start.sh restart  # 重启服务
#   ./start.sh status   # 查看服务运行状态与健康检查
#   ./start.sh logs     # 实时查看后台日志 (tail -f)
# ==============================================================================

set -e

# 确保在 agent_control 项目目录下执行
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${DIR}"

PID_FILE="${DIR}/logs/agent_control.pid"
LOG_FILE="${DIR}/logs/agent_control.log"
mkdir -p "${DIR}/logs"

# 优先选择虚拟环境中的可执行文件
if [ -f "${DIR}/venv/bin/uvicorn" ]; then
    UVICORN_BIN="${DIR}/venv/bin/uvicorn"
    PYTHON_BIN="${DIR}/venv/bin/python"
else
    UVICORN_BIN="uvicorn"
    PYTHON_BIN="python3"
fi

# 从 .env 读取配置 (若存在)
HOST="0.0.0.0"
PORT="8000"
if [ -f "${DIR}/.env" ]; then
    ENV_HOST=$(grep -E '^HOST=' "${DIR}/.env" | cut -d '=' -f2 | tr -d ' "' | tr -d "'")
    ENV_PORT=$(grep -E '^PORT=' "${DIR}/.env" | cut -d '=' -f2 | tr -d ' "' | tr -d "'")
    [ -n "${ENV_HOST}" ] && HOST="${ENV_HOST}"
    [ -n "${ENV_PORT}" ] && PORT="${ENV_PORT}"
fi

# ANSI 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${BLUE}====================================================================${NC}"
    echo -e "${GREEN}       🚀 Agent Control Plane (FastAPI 控制面服务)${NC}"
    echo -e "${BLUE}====================================================================${NC}"
    echo -e "  • 监听地址:   ${YELLOW}http://${HOST}:${PORT}${NC}"
    echo -e "  • 控制台面板: ${YELLOW}http://localhost:${PORT}/dashboard${NC}"
    echo -e "  • 交互式文档: ${YELLOW}http://localhost:${PORT}/docs${NC}"
    echo -e "  • 健康检查:   ${YELLOW}http://localhost:${PORT}/health${NC}"
    echo -e "${BLUE}====================================================================${NC}"
}

check_port_conflict() {
    local occupied_pid
    occupied_pid=$(lsof -ti :${PORT} 2>/dev/null || true)
    if [ -n "${occupied_pid}" ]; then
        echo -e "${YELLOW}⚠️  检测到端口 ${PORT} 已被进程占用 (PID: ${occupied_pid})，正在清理...${NC}"
        kill -15 ${occupied_pid} 2>/dev/null || true
        sleep 1
        kill -9 ${occupied_pid} 2>/dev/null || true
        sleep 0.5
        echo -e "${GREEN}✓ 端口 ${PORT} 已清理就绪。${NC}"
    fi
}

start_foreground() {
    print_banner
    check_port_conflict
    echo -e "${GREEN}▶ 以开发模式启动 (支持热重载，按 Ctrl+C 退出)...${NC}\n"
    exec "${UVICORN_BIN}" main:app --host "${HOST}" --port "${PORT}" --reload
}

start_daemon() {
    print_banner
    if [ -f "${PID_FILE}" ]; then
        local old_pid
        old_pid=$(cat "${PID_FILE}")
        if ps -p "${old_pid}" > /dev/null 2>&1; then
            echo -e "${YELLOW}服务已在后台运行中 (PID: ${old_pid})。${NC}"
            echo -e "可使用 ${BLUE}./start.sh restart${NC} 重启或 ${BLUE}./start.sh logs${NC} 查看日志。"
            exit 0
        fi
    fi

    check_port_conflict
    echo -e "${GREEN}▶ 正在启动后台守护进程...${NC}"
    nohup "${UVICORN_BIN}" main:app --host "${HOST}" --port "${PORT}" >> "${LOG_FILE}" 2>&1 &
    local new_pid=$!
    echo "${new_pid}" > "${PID_FILE}"
    sleep 1.5

    if ps -p "${new_pid}" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 启动成功！进程 PID: ${new_pid}${NC}"
        echo -e "  • 日志文件: ${LOG_FILE}"
        echo -e "  • 查看日志: ./start.sh logs"
        echo -e "  • 停止服务: ./start.sh stop\n"
    else
        echo -e "${RED}✗ 启动失败，请检查日志: ${LOG_FILE}${NC}"
        cat "${LOG_FILE}" | tail -n 20
        exit 1
    fi
}

stop_service() {
    echo -e "${YELLOW}▶ 正在停止 Agent Control 服务...${NC}"
    local stopped=0

    if [ -f "${PID_FILE}" ]; then
        local pid
        pid=$(cat "${PID_FILE}")
        if ps -p "${pid}" > /dev/null 2>&1; then
            kill -15 "${pid}" 2>/dev/null || true
            for _ in {1..5}; do
                if ! ps -p "${pid}" > /dev/null 2>&1; then
                    break
                fi
                sleep 0.5
            done
            kill -9 "${pid}" 2>/dev/null || true
            stopped=1
        fi
        rm -f "${PID_FILE}"
    fi

    # 清理端口残留
    local port_pids
    port_pids=$(lsof -ti :${PORT} 2>/dev/null || true)
    if [ -n "${port_pids}" ]; then
        kill -9 ${port_pids} 2>/dev/null || true
        stopped=1
    fi

    if [ ${stopped} -eq 1 ]; then
        echo -e "${GREEN}✓ 服务已成功停止。${NC}"
    else
        echo -e "${YELLOW}未发现运行中的服务实例。${NC}"
    fi
}

show_status() {
    local running=0
    local pid=""
    if [ -f "${PID_FILE}" ]; then
        pid=$(cat "${PID_FILE}")
        if ps -p "${pid}" > /dev/null 2>&1; then
            running=1
        fi
    fi

    local port_pid
    port_pid=$(lsof -ti :${PORT} 2>/dev/null | head -n 1 || true)
    if [ -n "${port_pid}" ]; then
        running=1
        [ -z "${pid}" ] && pid="${port_pid}"
    fi

    if [ ${running} -eq 1 ]; then
        echo -e "${GREEN}● Agent Control 运行中${NC} (PID: ${pid}, 端口: ${PORT})"
        local health_res
        health_res=$(curl -s "http://127.0.0.1:${PORT}/health" 2>/dev/null || true)
        if [ -n "${health_res}" ]; then
            echo -e "  • 健康状态: ${GREEN}${health_res}${NC}"
        else
            echo -e "  • 健康状态: ${YELLOW}应用尚未完全响应 HTTP 请求${NC}"
        fi
    else
        echo -e "${RED}○ Agent Control 未运行${NC}"
    fi
}

show_logs() {
    if [ -f "${LOG_FILE}" ]; then
        tail -f -n 50 "${LOG_FILE}"
    else
        echo -e "${YELLOW}日志文件 ${LOG_FILE} 尚不存在。${NC}"
    fi
}

# 命令分发
ACTION="${1:-dev}"

case "${ACTION}" in
    dev|"")
        start_foreground
        ;;
    start|daemon|-d|--daemon)
        start_daemon
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        sleep 1
        start_daemon
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|-h|--help)
        echo "用法: $0 [dev|start|stop|restart|status|logs]"
        echo "  dev      - 开发模式 (默认，前台运行，带热重载)"
        echo "  start    - 后台守护进程模式运行"
        echo "  stop     - 停止服务"
        echo "  restart  - 重启服务"
        echo "  status   - 查看运行状态"
        echo "  logs     - 实时查看后台日志"
        ;;
    *)
        echo -e "${RED}未知命令: ${ACTION}${NC}"
        echo "用法: $0 [dev|start|stop|restart|status|logs]"
        exit 1
        ;;
esac

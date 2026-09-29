#!/usr/bin/env python3
"""
Agent Control 本地调度守护 Worker
根据 task_schedules 中的 Cron 表达式与配置，在到达指定时间时自动触发任务执行。
"""

import sys
import os
import time
import subprocess
import logging
from datetime import datetime

# 注入工程路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
AGENT_CONTROL = os.path.join(PROJECT_ROOT, "agent_control")
if AGENT_CONTROL not in sys.path:
    sys.path.insert(0, AGENT_CONTROL)

from db.session import SessionLocal
from app.models.schedule import TaskSchedule, ScheduleRun
from app.core.security import generate_ulid

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [scheduler-worker]: %(message)s"
)
logger = logging.getLogger("scheduler-worker")

def match_cron_field(field_str: str, current_val: int) -> bool:
    if field_str == "*":
        return True
    for part in field_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "/" in part:
            sub, step = part.split("/", 1)
            step = int(step)
            start = 0 if sub == "*" else int(sub)
            if (current_val - start) % step == 0 and current_val >= start:
                return True
        elif "-" in part:
            start, end = map(int, part.split("-", 1))
            if start <= current_val <= end:
                return True
        elif part.isdigit() and int(part) == current_val:
            return True
    return False

def matches_cron(cron_expr: str, dt: datetime) -> bool:
    if not cron_expr:
        return False
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return False
    min_str, hr_str, dom_str, mon_str, dow_str = parts
    if not match_cron_field(min_str, dt.minute):
        return False
    if not match_cron_field(hr_str, dt.hour):
        return False
    if not match_cron_field(dom_str, dt.day):
        return False
    if not match_cron_field(mon_str, dt.month):
        return False
    cron_dow = (dt.weekday() + 1) % 7
    if dow_str != "*" and not (match_cron_field(dow_str, cron_dow) or (cron_dow == 0 and match_cron_field(dow_str, 7))):
        return False
    return True

def check_and_run_schedules():
    db = SessionLocal()
    now = datetime.now()

    try:
        schedules = db.query(TaskSchedule).filter(TaskSchedule.enabled == True).all()
        for s in schedules:
            if not s.cron_expression:
                continue

            if matches_cron(s.cron_expression, now):
                # 避免同分钟内重复执行
                if s.last_run_at and s.last_run_at.date() == now.date() and s.last_run_at.hour == now.hour and s.last_run_at.minute == now.minute:
                    continue

                logger.info(f"Triggering scheduled task: {s.name} ({s.cron_expression})")
                s.last_run_at = now
                db.commit()

                # 优先使用 agent_control 虚拟环境 python (含 requests, sqlalchemy 等库)
                venv_python = os.path.join(AGENT_CONTROL, "venv", "bin", "python3")
                raw_cmd = s.task_template.get("command", "python3 .agents/skills/hz-talent-crawler/scripts/crawler.py --days 3 --per-day 80")
                if os.path.exists(venv_python):
                    cmd = raw_cmd.replace("python3 ", f"{venv_python} ")
                else:
                    cmd = raw_cmd

                ret = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT)

                run_rec = ScheduleRun(
                    public_id=generate_ulid("SRUN"),
                    schedule_id=s.id,
                    scheduled_for=now,
                    triggered_at=now,
                    status="created" if ret.returncode == 0 else "failed",
                    message="Triggered successfully" if ret.returncode == 0 else f"Failed with exit code {ret.returncode}"
                )
                db.add(run_rec)
                db.commit()
    except Exception as e:
        logger.error(f"Scheduler worker error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Agent Control Scheduler Worker started. Monitoring schedules...")
    while True:
        check_and_run_schedules()
        time.sleep(30)

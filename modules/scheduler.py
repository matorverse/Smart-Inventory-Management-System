"""
Smart Inventory & Expiry Management System
FILE: modules/scheduler.py
PURPOSE: Background thread that runs expiry check daily.
"""

import threading
import schedule
import time
from datetime import datetime


_scheduler_thread = None
_running = False


def _run_scheduler():
    while _running:
        schedule.run_pending()
        time.sleep(60)


def start_scheduler(expiry_check_fn, on_alert_fn=None):
    """
    Starts the background expiry scheduler.

    Args:
        expiry_check_fn: Callable — the run_expiry_check function
        on_alert_fn:     Optional callable(count) called after each check
    """
    global _scheduler_thread, _running

    def job():
        try:
            count = expiry_check_fn()
            ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[Scheduler] {ts} — Expiry check ran. Batches logged: {count}")
            if on_alert_fn and count and count > 0:
                on_alert_fn(count)
        except Exception as e:
            print(f"[Scheduler ERROR] {e}")

    schedule.every().day.at("00:00").do(job)

    _running = True
    _scheduler_thread = threading.Thread(target=_run_scheduler, daemon=True)
    _scheduler_thread.start()
    print("[Scheduler] Background expiry check started (runs daily at midnight).")


def stop_scheduler():
    """Stops the background scheduler."""
    global _running
    _running = False
    schedule.clear()
    print("[Scheduler] Stopped.")

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def sample_cron_task():
    logger.info("[Scheduler] Heartbeat cron executed.")

def start_scheduler():
    scheduler.add_job(
        sample_cron_task,
        trigger=CronTrigger(minute="*/5"),
        id="sample_heartbeat",
        replace_existing=True
    )
    scheduler.start()
    logger.info("APScheduler initialized and running.")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler shut down.")

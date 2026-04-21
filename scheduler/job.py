import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.agent_runner import run_agent_async
from config import SCHEDULE_INTERVAL_MINUTES

logger = logging.getLogger(__name__)


async def agent_job():
    logger.info("[SCHEDULER] Starting scheduled agent run...")
    try:
        findings = await run_agent_async()
        logger.info("[SCHEDULER] Run complete. %d findings stored.", len(findings))
    except BaseException as e:
        logger.error("[SCHEDULER] Agent run failed: %s", e)
        if hasattr(e, "__notes__"):
            logger.error("[SCHEDULER] Notes: %s", e.__notes__)
        if hasattr(e, "exceptions"):
            for sub in e.exceptions:
                logger.error("[SCHEDULER] Sub-exception: %s", sub, exc_info=sub)


def start_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        agent_job,
        trigger="interval",
        minutes=SCHEDULE_INTERVAL_MINUTES,
        id="agent_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("[SCHEDULER] Scheduler started — runs every %d minute(s).", SCHEDULE_INTERVAL_MINUTES)
    return scheduler

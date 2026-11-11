import logging
import socket
import sys
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from digitalmarketing.tasks import run_pipeline
from .google_form_sync import import_all_google_forms

logger = logging.getLogger(__name__)

# Keep a reference to the socket so it doesn't get garbage collected
_scheduler_lock_socket = None

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

def start():
    global _scheduler_lock_socket
    
    # Don't start the scheduler during database migrations or other commands
    if 'makemigrations' in sys.argv or 'migrate' in sys.argv or 'collectstatic' in sys.argv:
        return

    try:
        # This socket binding prevents multiple scheduler instances from running 
        # in the background when multiple web server workers (like Gunicorn) are spawned.
        _scheduler_lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _scheduler_lock_socket.bind(("127.0.0.1", 47200)) # Bind to a random port
    except socket.error:
        # Another instance is already bound and running. 
        # We safely skip starting another scheduler.
        logger.debug("Scheduler is already running in another worker process.")
        return

    scheduler = BackgroundScheduler(timezone=getattr(settings, 'TIME_ZONE', 'UTC'))
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Schedule the pipeline to run every 10 minutes for testing
    scheduler.add_job(
        run_pipeline,
        trigger=CronTrigger(minute="*/10"),  # Runs every 10 minutes
        id="resume_pipeline_job",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'resume_pipeline_job'.")


    try:
        logger.info("Starting scheduler...")

        scheduler.add_job(
            import_all_google_forms,
            trigger=CronTrigger(minute="*/1"),
            id="google_form_import_job",
            replace_existing=True,
            max_instances=1,
        )


        logger.info("Scheduler started successfully")

    except Exception as e:
        logger.exception(f"Scheduler Error: {e}")
    
   

    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added weekly job: 'delete_old_job_executions'.")

    try:
        logger.info("Starting background scheduler...")
        scheduler.start()
    except Exception as e:
        logger.error(f"Scheduler failed to start: {e}")

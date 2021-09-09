from apscheduler.events import EVENT_JOB_REMOVED
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings
import logging

log = logging.getLogger('log')

class Scheduler(BackgroundScheduler):
    def __init__(self) -> None:
        tz = timezone(settings.TIME_ZONE)
        jobstores = {
            'default': DjangoJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 3
        }

        super().__init__(jobstores=jobstores, executors=executors,
                         job_defaults=job_defaults, timezone=tz)

scheduler = Scheduler()
scheduler.start()

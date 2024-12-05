from . import BackgroundScheduler
from . import CronTrigger
from . import Callable
from . import uuid
from . import pytz

class object_scheduler:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()
        self.job_id = ''
        self.job_sql_id = ''

    def __get_scheduler(self) -> BackgroundScheduler:
        return self.scheduler

    def __get_current_job_sql_id(self) -> str:
        return self.job_sql_id

    def __get_current_job_id(self) -> str:
        return self.job_id

    def get_job_status(self) -> bool:
        return self.__get_scheduler().get_jobs()
    
    def get_background_jobs(self) -> list:
        return [
            {
                'id': job.id,
                'trigger': str(job.trigger),
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
            } 
            
            for job in self.__get_scheduler().get_jobs()
        ]
    
    def __set_job_id(self, id: str) -> None:
        self.job_id = id

    def __set_job_sql_id(self, id: str) -> None:
        self.job_sql_id = id

    def set_background_job_removal(self) -> bool:
        scheduler = self.__get_scheduler()
        scheduler.remove_all_jobs()

    def set_background_job(self, methods: list[Callable], interval: str, interval_len: str = 'days') -> None:
        scheduler = self.__get_scheduler()

        self.set_background_job_removal()
        self.__set_job_id(str(uuid.uuid4()))
        self.__set_job_sql_id(str(uuid.uuid4()))

        if interval_len == 'days':
            scheduler.add_job(methods[0], 'interval', days = int(interval), max_instances=1, id = self.__get_current_job_id())
            scheduler.add_job(methods[1], 'interval', days = int(interval), max_instances=1, id = self.__get_current_job_sql_id())
        else:
            #-- for debugging only
            scheduler.add_job(methods[0], 'interval', minutes = int(interval), max_instances=1, id = self.__get_current_job_id())
            scheduler.add_job(methods[1], 'interval', minutes = int(interval), max_instances=1, id = self.__get_current_job_sql_id())

        scheduler.start()

    def set_background_with_specific_date_job(self, methods: list[Callable], hour: int) -> None:
        scheduler = self.__get_scheduler()

        self.set_background_job_removal()
        self.__set_job_id(str(uuid.uuid4()))
        self.__set_job_sql_id(str(uuid.uuid4()))

        scheduler.add_job(methods[0], CronTrigger(hour = hour, minute = 0, timezone = pytz.timezone('Asia/Jakarta')), id = self.__get_current_job_id())
        scheduler.add_job(methods[1], CronTrigger(hour = hour, minute = 0, timezone = pytz.timezone('Asia/Jakarta')), id = self.__get_current_job_sql_id())

        scheduler.start()

    def set_midnight_background_job(self, methods: list[Callable]) -> None:
        scheduler = self.__get_scheduler()

        self.set_background_job_removal()
        self.__set_job_id(str(uuid.uuid4()))
        self.__set_job_sql_id(str(uuid.uuid4()))

        scheduler.add_job(methods[0], CronTrigger(hour=0, minute=0), id = self.__get_current_job_id())
        scheduler.add_job(methods[1], CronTrigger(hour=0, minute=0), id = self.__get_current_job_sql_id())

        scheduler.start()
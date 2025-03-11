from . import BackgroundScheduler
from . import CronTrigger
from . import Callable
from . import uuid
from . import pytz

class object_scheduler:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Jakarta'))
        self.job_id = ''
        self.job_sql_id = ''
        self.job_oauth_id = ''

        self.scheduler.start()

    def __get_scheduler(self) -> BackgroundScheduler:
        return self.scheduler

    def __get_current_job_sql_id(self) -> str:
        return self.job_sql_id
    
    def __get_current_job_oauth_id(self) -> str:
        return self.job_oauth_id

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
    
    def get_backup_jobs(self) -> list:
        return [
            {
                'id': job.id,
                'trigger': str(job.trigger),
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
            } 
            
            for job in self.__get_scheduler().get_jobs() if (job.id == self.__get_current_job_sql_id() or job.id == self.__get_current_job_id())
        ]
    
    def __set_job_id(self, id: str) -> None:
        self.job_id = id

    def __set_job_sql_id(self, id: str) -> None:
        self.job_sql_id = id

    def __set_job_oauth_id(self, id: str) -> None:
        self.job_oauth_id = id

    def __set_all_background_job_removal(self) -> bool:
        scheduler = self.__get_scheduler()
        scheduler.remove_all_jobs()

    def __set_background_job_removal(self, job_id: str) -> bool:
        scheduler = self.__get_scheduler()

        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
    
    def __set_new_backup_jobs_config(self) -> None:
        self.__set_background_job_removal(self.__get_current_job_id())
        self.__set_background_job_removal(self.__get_current_job_sql_id())

        if not self.__get_current_job_id():
            self.__set_job_id(str(uuid.uuid4()))

        if not self.__get_current_job_sql_id():
            self.__set_job_sql_id(str(uuid.uuid4()))
    
    def set_backup_background_job_removal(self) -> bool:
        self.__set_background_job_removal(self.__get_current_job_id())
        self.__set_background_job_removal(self.__get_current_job_sql_id())

    def set_oauth_background_job(self, methods: Callable) -> None:
        scheduler = self.__get_scheduler()

        if scheduler.running == False:
            scheduler.start()

        self.__set_background_job_removal(self.__get_current_job_oauth_id())

        if not self.__get_current_job_oauth_id():
            self.__set_job_oauth_id(str(uuid.uuid4()))

        scheduler.add_job(methods, 'interval', minutes = 45, max_instances=1, id = self.__get_current_job_oauth_id())

    def set_background_job(self, methods: list[Callable], interval: str, interval_len: str = 'days') -> None:
        scheduler = self.__get_scheduler()

        if scheduler.running == False:
            scheduler.start()

        self.__set_new_backup_jobs_config()

        if interval_len == 'days':
            scheduler.add_job(methods[0], 'interval', days = int(interval), max_instances = 1, id = self.__get_current_job_id())
            scheduler.add_job(methods[1], 'interval', days = int(interval), max_instances = 1, id = self.__get_current_job_sql_id())
        else:
            #-- for debugging only
            scheduler.add_job(methods[0], 'interval', minutes = int(interval), max_instances = 1, id = self.__get_current_job_id())
            scheduler.add_job(methods[1], 'interval', minutes = int(interval), max_instances = 1, id = self.__get_current_job_sql_id())

    def set_background_with_specific_date_job(self, methods: list[Callable], hour: int) -> None:
        scheduler = self.__get_scheduler()

        if scheduler.running == False:
            scheduler.start()

        self.__set_new_backup_jobs_config()

        scheduler.add_job(methods[0], CronTrigger(hour = hour, minute = 0, timezone = pytz.timezone('Asia/Jakarta')), max_instances = 1, id = self.__get_current_job_id())
        scheduler.add_job(methods[1], CronTrigger(hour = hour, minute = 0, timezone = pytz.timezone('Asia/Jakarta')), max_instances = 1, id = self.__get_current_job_sql_id())
import os
import logging
import paramiko

from flask import Flask
from flask import request
from dotenv import load_dotenv

from Objects import object_backup as system_backup
from Objects import object_scheduler as backup_scheduler
from Commons import commons_global as globals

#-- load env
load_dotenv(override=True)

#-- initialize variables
app = Flask(__name__)
debug = False
prefix = 'backup'
agenda = backup_scheduler.object_scheduler()

backup = system_backup.object_backup(
    os.getenv("BACKUP_EMAIL"), 
    os.getenv("BACKUP_FOLDER_ID"), 
    os.getenv("BACKUP_FOLDER_ID_DATABASE"), 
    os.getenv("BACKUP_FOLDER_TARGET")
)

backup_sql = system_backup.object_backup_sql(backup)

agenda.set_oauth_background_job(backup.set_new_oauth_access_token)

@app.route(f'/{prefix}', methods= ['GET'])
def check_api():
    try:
        return globals.response.get_api_response(200, "Backup API is alive")
    
    except Exception as err:
        return globals.response.get_api_response(501, err)

@app.route(f'/{prefix}/set_backup', methods= ['GET'])
def set_backup():
    try:
        backup_sql.set_system_backup()
        return globals.response.get_api_response(200, "Successfully Backed up folder!")
    
    except Exception as err:
        return globals.response.get_api_response(501, str(err))
    
@app.route(f'/{prefix}/set_backup_database', methods= ['GET'])
def set_backup_database():
    try:
        backup_sql.set_database_backup()
        return globals.response.get_api_response(200, "Successfully Backed up database!")
    
    except Exception as err:
        return globals.response.get_api_response(501, str(err))

@app.route(f'/{prefix}/start/daily/midnight', methods= ['POST'])
def start_periodic_midnight_backup():
    try:
        if len(agenda.get_background_jobs()) > 1:
            return globals.response.get_api_response(200, "periodic backup has already been started")
        
        agenda.set_midnight_background_job([backup_sql.set_system_backup, backup_sql.set_database_backup])
        return globals.response.get_api_response(200, "Successfully started periodic backup every midnight! Please wait and check the job before stopping any jobs")
    
    except Exception as err:
        return globals.response.get_api_response(501, str(err))
    
@app.route(f'/{prefix}/start/daily/<int:hour>', methods= ['POST'])
def start_periodic_daily_backup(hour: int):
    try:
        if len(agenda.get_background_jobs()) > 1:
            return globals.response.get_api_response(200, "periodic backup has already been started")
        
        agenda.set_background_with_specific_date_job([backup_sql.set_system_backup, backup_sql.set_database_backup], int(hour))
        return globals.response.get_api_response(200, f'Successfully started daily backup at {hour}:00 WIB ! Please wait and check the job before stopping any jobs')
    
    except Exception as err:
        return globals.response.get_api_response(501, str(err))

@app.route(f'/{prefix}/start', methods= ['POST'])
def start_periodic_backup():
    try:
        if len(agenda.get_background_jobs()) > 1:
            return globals.response.get_api_response(200, "periodic backup has already been started! Please wait and check the job before stopping any jobs")
        
        data = request.get_json()
        interval = data['interval']
        interval_type = data['interval_type']
        
        agenda.set_background_job([backup_sql.set_system_backup, backup_sql.set_database_backup], interval, interval_len = interval_type)

        return globals.response.get_api_response(200, f"Successfully Started Periodic backup for {interval} {interval_type}!")
    
    except Exception as err:
        return globals.response.get_api_response(501, str(err))

@app.route(f'/{prefix}/stop', methods= ['POST'])
def stop_periodic_backup():
    try:
        if len(agenda.get_background_jobs()) == 0:
            return globals.response.get_api_response(200, "Periodic backup has not been started")
        
        agenda.set_backup_background_job_removal()
        return globals.response.get_api_response(200, "Periodic backup has been stopped")
    
    except Exception as err:
        return globals.response.get_api_response(501, str(err))

@app.route(f'/{prefix}/check', methods= ['GET'])
def check_periodic_backup():
    try:
        jobs = agenda.get_background_jobs()
        return globals.response.get_api_response(200, jobs)
    
    except Exception as err:
        return globals.response.get_api_response(501, str(err))
    
@app.route(f'/{prefix}/refresh_oauth_token', methods= ['GET'])
def refresh_oauth_token():
    try:
        backup.set_new_oauth_access_token()
        return globals.response.get_api_response(200, 'Token has been renewed!')
    
    except Exception as err:
        return globals.response.get_api_response(501, str(err))

if __name__ == '__main__':
    #-- check status
    if (os.getenv("APP_STATUS") == 'development'):
        paramiko.util.log_to_file("paramiko.log", level=logging.DEBUG)

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("paramiko")
        logger.setLevel(logging.DEBUG)

        debug = True

    #-- run app
    app.run(host = '0.0.0.0', debug = debug)
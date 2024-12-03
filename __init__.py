import os

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

@app.route(f'/{prefix}/start', methods= ['POST'])
def start_periodic_backup():
    try:
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
        response = agenda.set_background_job_removal()
        message = "Periodic backup has not been started"
        if (response):
            message = "Periodic backup has been stopped"

        return globals.response.get_api_response(200, message)
    
    except Exception as err:
        return globals.response.get_api_response(501, str(err))

@app.route(f'/{prefix}/check', methods= ['GET'])
def check_periodic_backup():
    try:
        message = f'Periodic backup has not been started'
        if (agenda.get_job_status()):
            message = f'Periodic backup has started'

        return globals.response.get_api_response(200, message)
    
    except Exception as err:
        return globals.response.get_api_response(501, str(err))

if __name__ == '__main__':
    #-- check status
    if (os.getenv("APP_STATUS") == 'development'):
       debug = True

    #-- run app
    app.run(host = '0.0.0.0', debug = debug)
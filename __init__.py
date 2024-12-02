import os

from flask import Flask
from dotenv import load_dotenv

from Commons import commons_variables as variables
from Commons import commons_global as globals

load_dotenv(override=True)

prefix = 'backup'
app = Flask(__name__)

@app.route(f'/{prefix}', methods= ['GET'])
def check_api():
    try:
        return globals.response.get_api_response(200, "Backup API is alive")
    except Exception as e:
        return globals.response.get_api_response(501, "Somethings Not Right!")

@app.route(f'/{prefix}/set_backup', methods= ['GET'])
def set_backup():
    try:
        variables.backup.__set_backup()
        return globals.response.get_api_response(200, "Successfully Backed up folder!")
    
    except Exception as e:
        return globals.response.get_api_response(501, "Somethings Not Right!")

@app.route(f'/{prefix}/start', methods= ['POST'])
def start_periodic_backup():
    return globals.response.get_api_response(200, "Coming Soon!")

@app.route(f'/{prefix}/stop', methods= ['POST'])
def stop_periodic_backup():
    return globals.response.get_api_response(200, "Coming Soon!")

if __name__ == '__main__':
    debug = False

    if (os.getenv("APP_STATUS") == 'development'):
       debug = True

    app.run(host = '0.0.0.0', debug = debug)
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

SERVICE_ACCOUNT_FILE = "service_account.json"

SCOPES = ['https://www.googleapis.com/auth/drive.file']

credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)

gauth = GoogleAuth()
gauth.credentials = credentials

drive = GoogleDrive(gauth)

FOLDER_ID = '1HCMYpRf_FjaNeN77p-MFRIcD7tR_qISe'

file = drive.CreateFile({'title': 'dockerfile', 'parents': [{'id': FOLDER_ID}]})
file.SetContentFile('dockerfile')
file.Upload()

print(f"Uploaded file with ID: {file['id']}")

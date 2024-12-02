from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

SERVICE_ACCOUNT_FILE = "service_account.json"

SCOPES = ['https://www.googleapis.com/auth/drive.file']

credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)

gauth = GoogleAuth()
gauth.credentials = credentials

drive = GoogleDrive(gauth)

folder_name = "My Shared Folder 1"
folder_metadata = {
    'title': folder_name,
    'mimeType': 'application/vnd.google-apps.folder'
}

folder = drive.CreateFile(folder_metadata)
folder.Upload()

print(f"Created folder '{folder_name}' with ID: {folder['id']}")

your_email = "fairuz.akbar.azaria@gmail.com"
permission = {
    'type': 'user',
    'value': your_email,
    'role': 'writer'
}
folder.InsertPermission(permission)

print(f"Shared folder '{folder_name}' with email: {your_email}")

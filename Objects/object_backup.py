from Objects import os
from Objects import pytz
from Objects import shutil
from Objects import datetime
from Objects import GoogleAuth
from Objects import GoogleDrive
from Objects import load_dotenv
from Objects import Credentials

from Commons import commons_global as globals

load_dotenv(override=True)

class object_backup:
    def __init__(self, email: str, backup_folder_id: str, folder_to_backup: str) -> None:
        self.type = os.getenv("GDRIVE_ACC_TYPE")
        self.project_id = os.getenv("GDRIVE_PROJECT_ID")
        self.private_key_id = os.getenv("GDRIVE_PRIVATE_KEY_ID")
        self.private_key = os.getenv("GDRIVE_PRIVATE_KEY")
        self.client_email = os.getenv("GDRIVE_EMAIL")
        self.client_id = os.getenv("GDRIVE_CLIENT_ID")
        self.auth_uri = os.getenv("GDRIVE_AUTH_URI")
        self.token_uri = os.getenv("GDRIVE_TOKEN_URI")
        self.auth_provider_cert_url = os.getenv("GDRIVE_AUTH_PROVIDER_CERT")
        self.client_cert_url = os.getenv("GDRIVE_CLIENT_CERT")
        self.universe_domain = os.getenv("GDRIVE_UNIVERSE_DOMAIN")
        
        self.email = email
        self.backup_folder_id = backup_folder_id
        self.folder_to_backup = folder_to_backup
        self.folder_temp_dir = 'Backups'
        self.scope = ['https://www.googleapis.com/auth/drive.file']

    def __get_folder_temp_dir(self) -> str:
        return self.folder_temp_dir

    def __get_folder_to_backup(self) -> str:
        return self.folder_to_backup

    def __get_backup_folder_id(self) -> str:
        return self.backup_folder_id

    def __get_type(self) -> str:
        return self.type
    
    def __get_project_id(self) -> str:
        return self.project_id
    
    def __get_private_key_id(self) -> str:
        return self.private_key_id
    
    def __get_private_key(self) -> str:
        return self.private_key
    
    def __get_client_email(self) -> str:
        return self.client_email
    
    def __get_client_id(self) -> str:
        return self.client_id
    
    def __get_auth_uri(self) -> str:
        return self.auth_uri
    
    def __get_token_uri(self) -> str:
        return self.token_uri
    
    def __get_auth_provider_cert_url(self) -> str:
        return self.auth_provider_cert_url
    
    def __get_client_cert_url(self) -> str:
        return self.client_cert_url
    
    def __get_universe_domain(self) -> str:
        return self.universe_domain
    
    def __get_scope(self) -> list:
        return self.scope

    def __get_email(self) -> str:
        return self.email
    
    def __get_gauth_credentials(self) -> Credentials:
        return Credentials.from_service_account_info(self.__get_config(), scopes = self.__get_scope())
    
    def __get_drive(self, credentials: Credentials) -> GoogleDrive:
        gauth = GoogleAuth()
        gauth.credentials = credentials

        return GoogleDrive(gauth)
    
    def __get_backup_name(self, timezone: str = 'Asia/Jakarta') -> str:
        today = str(datetime.now(pytz.timezone(timezone)).replace(tzinfo=None,microsecond=0)).split(' ')
        current_date = '_'.join(today)

        return current_date

    def __get_config(self) -> dict:
        return globals.response.get_drive_service_account(
            self.__get_type(),
            self.__get_project_id(),
            self.__get_private_key_id(),
            self.__get_private_key(),
            self.__get_client_email(),
            self.__get_client_id(),
            self.__get_auth_uri(),
            self.__get_token_uri(),
            self.__get_auth_provider_cert_url(),
            self.__get_client_cert_url(),
            self.__get_universe_domain()
        )

    def __set_backup_folder_id(self, folder_id: str, folder_name: str) -> dict:
        if self.__get_backup_folder_id():
            google_creds = self.__get_gauth_credentials()
            google_drive = self.__get_drive(google_creds)

            folder_metadata = globals.response.get_drive_folder_metadata(folder_name)
            folder = google_drive.CreateFile(folder_metadata)
            folder.Upload()

            permission = globals.response.get_drive_folder_permission('user', self.__get_email(), 'writer')
            folder.InsertPermission(permission)

            folder_id = folder['id']

        self.backup_folder_id = folder_id
        
    def __set_backup(self) -> None:
        google_creds = self.__get_gauth_credentials()
        google_drive = self.__get_drive(google_creds)
        
        file_name = self.__get_backup_name()
        self.__set_backup_file(file_name)

        file_backup = os.path.join(self.__get_folder_temp_dir(), file_name)
        file_metadata = globals.response.get_drive_file_format('', [{ 'id': self.__get_backup_folder_id() }])

        backup = google_drive.CreateFile(file_metadata)
        backup.SetContentFile(file_backup)
        backup.Upload()

    def __set_backup_file(self, file_name: str, compression: str = 'tar') -> None:
        file_path = os.path.join(self.__get_folder_temp_dir(), file_name)
        shutil.make_archive(file_path, compression, self.__get_folder_to_backup())

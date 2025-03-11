from Objects import os
from Objects import io
from Objects import time
from Objects import pytz
from Objects import shutil
from Objects import pymysql
from Objects import paramiko
from Objects import datetime
from Objects import sshtunnel
from Objects import GoogleAuth
from Objects import GoogleDrive
from Objects import load_dotenv
from Objects import ServiceAccountCredentials

from Objects import dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from Commons import commons_global as globals

#-- load env
load_dotenv(override=True)

class object_backup:
    def __init__(self, email: str, backup_folder_id: str, backup_folder_id_database:str, folder_to_backup: str) -> None:
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
        self.backup_folder_id_database = backup_folder_id_database
        self.folder_to_backup = folder_to_backup
        self.folder_temp_dir = 'Backups'
        self.scope = ['https://www.googleapis.com/auth/drive.file']

    def __get_folder_temp_dir(self) -> str:
        return self.folder_temp_dir

    def __get_folder_to_backup(self) -> str:
        return self.folder_to_backup

    def __get_backup_folder_id(self) -> str:
        return self.backup_folder_id
    
    def __get_backup_folder_id_database(self) -> str:
        return self.backup_folder_id_database

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
    
    def __get_gauth_credentials(self) -> ServiceAccountCredentials:
        return ServiceAccountCredentials.from_json_keyfile_dict(self.__get_config(), scopes = self.__get_scope())
    
    def __get_drive(self, credentials: ServiceAccountCredentials) -> GoogleDrive:
        gauth = GoogleAuth()
        gauth.credentials = credentials

        return GoogleDrive(gauth)
    
    def __get_backup_name(self, timezone: str = 'Asia/Jakarta') -> str:
        today = str(datetime.now(pytz.timezone(timezone)).replace(tzinfo=None,microsecond=0)).replace(' ', '_').replace(':', '-')
        return today
    
    def __get_backup_database_name(self, timezone: str = 'Asia/Jakarta') -> str:
        today = str(datetime.now(pytz.timezone(timezone)).replace(tzinfo=None,microsecond=0)).replace(' ', '_').replace(':', '-')
        return f'{today}_sql'

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
    
    def __get_oauth_creds(self) -> Credentials:
        credentials = Credentials.from_authorized_user_info(self.__get_oauth_creds_config())
        credentials.refresh(Request())

        self.__set_oauth_creds_config(credentials)

        return credentials
    
    def __get_oauth_creds_config(self) -> dict:
        return globals.response.get_oauth_creds(
            os.getenv("CREDS_AUTH_TOKEN"), 
            os.getenv("CREDS_REFRESH_TOKEN"), 
            os.getenv("CREDS_AUTH_TOKEN_URI"), 
            os.getenv("CREDS_AUTH_CLIENT_ID"), 
            os.getenv("CREDS_AUTH_CLIENT_SECRETS"), 
            os.getenv("CREDS_AUTH_SCOPES"), 
            os.getenv("CREDS_AUTH_UNIVERSE_DOMAIN"), 
            os.getenv("CREDS_AUTH_ACCOUNT"), 
            os.getenv("CREDS_AUTH_TOKEN_EXPIRY")
        )
    
    def __set_oauth_creds_config(self, creds: Credentials, env_path: str = '.env') -> None:
        dotenv.set_key(env_path, "CREDS_AUTH_TOKEN", str(creds.token))
        dotenv.set_key(env_path, "CREDS_REFRESH_TOKEN", str(creds.refresh_token))
        dotenv.set_key(env_path, "CREDS_AUTH_TOKEN_URI", str(creds.token_uri))
        dotenv.set_key(env_path, "CREDS_AUTH_CLIENT_ID", str(creds.client_id))
        dotenv.set_key(env_path, "CREDS_AUTH_CLIENT_SECRETS", str(creds.client_secret))
        dotenv.set_key(env_path, "CREDS_AUTH_SCOPES", str(creds.scopes[0]))
        dotenv.set_key(env_path, "CREDS_AUTH_UNIVERSE_DOMAIN", str(creds.universe_domain))
        dotenv.set_key(env_path, "CREDS_AUTH_ACCOUNT", str(creds.account))
        dotenv.set_key(env_path, "CREDS_AUTH_TOKEN_EXPIRY", str(creds.expiry))

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

    def __set_backup_file(self, file_name: str, compression: str = 'tar') -> None:
        file_path = os.path.join(globals.system.get_root_dir(), self.__get_folder_temp_dir(), file_name)
        folder_to_backup = self.__get_folder_to_backup()

        shutil.make_archive(file_path, compression, folder_to_backup)

    def __set_backup_database_file(self, file_name: str, compression: str = 'tar') -> None:
        file_path = os.path.join(globals.system.get_root_dir(), self.__get_folder_temp_dir(), 'Database', f'{file_name}')
        folder_to_backup = os.path.join(globals.system.get_root_dir(), self.__get_folder_temp_dir(), 'Database')

        shutil.make_archive(file_path, compression, folder_to_backup)

    def __set_temp_backup_file_removal(self, file: str) -> None:
        if os.path.exists(file):
            os.remove(file)

    def set_backup(self, compression: str = 'tar') -> None:
        google_creds = self.__get_gauth_credentials()
        google_drive = self.__get_drive(google_creds)

        file_name = self.__get_backup_name()
        file_name_full = f'{file_name}.{compression}'
        self.__set_backup_file(file_name, compression = compression)

        file_backup = os.path.join(globals.system.get_root_dir(), self.__get_folder_temp_dir(), file_name_full)
        file_metadata = globals.response.get_drive_file_format(file_name_full, [{ 'id': self.__get_backup_folder_id() }])

        backup = google_drive.CreateFile(file_metadata)
        backup.SetContentFile(file_backup)
        backup.Upload()

        del backup
        self.__set_temp_backup_file_removal(file_backup)

    def set_backup_sql(self, compression: str = 'tar') -> None:
        google_creds = self.__get_gauth_credentials()
        google_drive = self.__get_drive(google_creds)

        file_name = self.__get_backup_database_name()
        file_name_full = f'{file_name}.{compression}'
        self.__set_backup_database_file(file_name, compression = compression)

        file_backup = os.path.join(globals.system.get_root_dir(), self.__get_folder_temp_dir(), 'Database', file_name_full)
        file_metadata = globals.response.get_drive_file_format(file_name_full, [{ 'id': self.__get_backup_folder_id_database() }])

        backup_sql = google_drive.CreateFile(file_metadata)
        backup_sql.SetContentFile(file_backup)
        backup_sql.Upload()

        del backup_sql
        self.__set_temp_backup_file_removal(file_backup)
    
    def set_backup_system(self, file_name: str) -> None:
        google_creds = self.__get_gauth_credentials()
        google_drive = self.__get_drive(google_creds)

        file_backup = os.path.join(globals.system.get_root_dir(), self.__get_folder_temp_dir(), file_name)
        file_metadata = globals.response.get_drive_file_format(file_name, [{ 'id': self.__get_backup_folder_id() }])

        backup_system = google_drive.CreateFile(file_metadata)
        backup_system.SetContentFile(file_backup)
        backup_system.Upload()

        del backup_system
        self.__set_temp_backup_file_removal(file_backup)

    def set_oauth_backup_system(self, file_name: str) -> None:
        creds = Credentials.from_authorized_user_info(self.__get_oauth_creds_config())
        creds.refresh(Request())

        self.__set_oauth_creds_config(creds)
    
        drive_service = build('drive', 'v3', credentials = creds)
        
        file_backup = os.path.join(globals.system.get_root_dir(), self.__get_folder_temp_dir(), file_name)
        file_metadata = {            
            'name': file_name, 
            'parents': [self.__get_backup_folder_id()]
        }

        file_media = MediaFileUpload(file_backup, resumable=True)

        file = drive_service.files().create(body = file_metadata, media_body = file_media, fields = 'id').execute()
    
    def set_oauth_backup_database(self, compression: str = 'tar') -> str:
        creds = Credentials.from_authorized_user_info(self.__get_oauth_creds_config())
        creds.refresh(Request())

        self.__set_oauth_creds_config(creds)
    
        drive_service = build('drive', 'v3', credentials = creds)

        file_name = self.__get_backup_database_name()
        file_name_full = f'{file_name}.{compression}'
        self.__set_backup_database_file(file_name, compression = compression)

        file_backup = os.path.join(globals.system.get_root_dir(), self.__get_folder_temp_dir(), 'Database', file_name_full)
        file_metadata = {            
            'name': file_name_full, 
            'parents': [self.__get_backup_folder_id_database()]
        }

        file_media = MediaFileUpload(file_backup, resumable=True)

        file = drive_service.files().create(body = file_metadata, media_body = file_media, fields = 'id').execute()

        return file_backup
    
    def set_new_oauth_access_token(self) -> None:
        creds = Credentials.from_authorized_user_info(self.__get_oauth_creds_config())
        creds.refresh(Request())

        self.__set_oauth_creds_config(creds)

class object_backup_sql:
    def __init__(self, backup_drive: object_backup) -> None:
        self.ssh_private_key = os.getenv("SSH_PRIVATE_KEY")
        self.ssh_username = os.getenv("SSH_USERNAME")
        self.ssh_host = os.getenv("SSH_HOST")
        self.ssh_port = os.getenv("SSH_PORT")

        self.db_host = os.getenv("SSH_DB_HOST")
        self.db_port = os.getenv("SSH_DB_PORT")
        self.db_name = os.getenv("SSH_DB_NAME")
        self.db_username = os.getenv("SSH_DB_USERNAME")
        self.db_password = os.getenv("SSH_DB_PASSWORD")

        self.db_name_2 = os.getenv("SSH_DB_NAME_2")
        self.db_username_2 = os.getenv("SSH_DB_USERNAME_2")
        self.db_password_2 = os.getenv("SSH_DB_PASSWORD_2")

        self.backup_drive = backup_drive

        self.folder_temp_dir = os.path.join(globals.system.get_root_dir(), 'Backups', 'Database')
        self.folder_temp_dir_server = f'/tmp/{os.getenv("SSH_DB_NAME")}_backup.sql'
        self.folder_temp_dir_server_2 = f'/tmp/{os.getenv("SSH_DB_NAME_2")}_backup.sql'

        self.folder_temp_dir_system = 'Backups'
        self.folder_temp_dir_system_server = os.getenv("BACKUP_FOLDER_TARGET_SYSTEM_TEMP")
        self.folder_temp_dir_system_server_target = os.getenv("BACKUP_FOLDER_TARGET_SYSTEM")

    def __get_folder_temp_dir_system(self) -> str:
        return self.folder_temp_dir_system

    def __get_folder_temp_dir_system_server(self) -> str:
        return self.folder_temp_dir_system_server
    
    def __get_folder_temp_dir_system_server_target(self) -> str:
        return self.folder_temp_dir_system_server_target

    def __get_backup_drive(self) -> object_backup:
        return self.backup_drive

    def __get_ssh_private_key(self) -> str:
        return self.ssh_private_key
    
    def __get_ssh_username(self) -> str:
        return self.ssh_username
    
    def __get_ssh_host(self) -> str:
        return self.ssh_host
    
    def __get_ssh_port(self) -> str:
        return self.ssh_port

    def __get_db_host(self) -> str:
        return self.db_port

    def __get_db_port(self) -> str:
        return self.db_host
    
    def __get_db_name_2(self) -> str:
        return self.db_name_2
    
    def __get_db_username_2(self) -> str:
        return self.db_username_2

    def __get_db_password_2(self) -> str:
        return self.db_password_2

    def __get_db_name(self) -> str:
        return self.db_name
    
    def __get_db_username(self) -> str:
        return self.db_username

    def __get_db_password(self) -> str:
        return self.db_password

    def __get_private_key(self) -> str:
        return self.ssh_private_key
    
    def __get_folder_temp_dir(self) -> str:
        return self.folder_temp_dir

    def __get_folder_temp_dir_server(self) -> str:
        return self.folder_temp_dir_server
    
    def __get_folder_temp_dir_server_2(self) -> str:
        return self.folder_temp_dir_server_2

    def __get_backup_name(self, timezone: str = 'Asia/Jakarta') -> str:
        today = str(datetime.now(pytz.timezone(timezone)).replace(tzinfo=None,microsecond=0)).replace(' ', '_').replace(':', '-')
        return today
    
    def __get_ssh_tunnel_conn(self) -> paramiko.SSHClient:
        private_key_content = self.__get_private_key()
        private_key_stream = io.StringIO(private_key_content)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.__get_ssh_host(), username=self.__get_ssh_username(), pkey=paramiko.Ed25519Key(file_obj=private_key_stream))

        return client

    def __get_database_backup(self, db_no: int, server: paramiko.SSHClient) -> str:
        if db_no == 1:
            file_name = f'{self.__get_backup_name()}_{self.__get_db_name()}.sql'
        elif db_no == 2:
            file_name = f'{self.__get_backup_name()}_{self.__get_db_name_2()}.sql'
            
        file_path = os.path.join(globals.system.get_root_dir(), self.__get_folder_temp_dir(), file_name)
        remote_path = self.__get_folder_temp_dir_server()

        server.get_transport().set_keepalive(30)

        with server.open_sftp() as sftp, open(file_path, 'wb') as f:
            file_size = sftp.stat(remote_path).st_size
            with sftp.file(remote_path, 'rb') as remote_file:
                chunk_size = 32768
                bytes_read = 0
                
                while True:
                    data = remote_file.read(chunk_size)
                    if not data:
                        break

                    f.write(data)
                    bytes_read += len(data)
                    print(f"Retrieving Database Backup, Downloaded {bytes_read} out of {file_size} bytes", end="\r")

        return file_path
    
    def __get_system_backup(self, server: paramiko.SSHClient) -> str:
        file_name = f'{self.__get_backup_name()}.tar.gz'
        local_path = os.path.join(globals.system.get_root_dir(), self.__get_folder_temp_dir_system(), file_name)
        remote_path = self.__get_folder_temp_dir_system_server()

        server.get_transport().set_keepalive(30)
        
        with server.open_sftp() as sftp, open(local_path, 'wb') as f:
            file_size = sftp.stat(remote_path).st_size
            with sftp.file(remote_path, 'rb') as remote_file:
                chunk_size = 32768
                bytes_read = 0
                
                while True:
                    data = remote_file.read(chunk_size)
                    if not data:
                        break

                    f.write(data)
                    bytes_read += len(data)
                    print(f"Retrieving System Backup, Downloaded {bytes_read} out of {file_size} bytes", end="\r")

        return file_name, local_path

    def __set_server_database_backup(self, db_no: int, server: paramiko.SSHClient) -> None:
        if db_no == 1:
            command = f"mysqldump -u {self.__get_db_username()} -p{self.__get_db_password()} {self.__get_db_name()} > {self.__get_folder_temp_dir_server()}"
        elif db_no == 2:
            command = f"mysqldump -u {self.__get_db_username_2()} -p{self.__get_db_password_2()} {self.__get_db_name_2()} > {self.__get_folder_temp_dir_server_2()}"

        stdin, stdout, stderr = server.exec_command(command)
        stdout.channel.recv_exit_status()

    def __set_server_system_backup(self, server: paramiko.SSHClient) -> None:
        compress_command = f"tar -czf {self.__get_folder_temp_dir_system_server()} -C {self.__get_folder_temp_dir_system_server_target()} ."
        stdin, stdout, stderr = server.exec_command(compress_command)
        stdout.channel.recv_exit_status()

    def set_database_backup(self, await_time: int = 5) -> None:   
        server = self.__get_ssh_tunnel_conn()

        self.__set_server_database_backup(1, server)
        time.sleep(await_time)

        self.__set_server_database_backup(2, server)
        time.sleep(await_time)

        file_path = self.__get_database_backup(1, server)
        file_path_2 = self.__get_database_backup(2, server)

        server.exec_command(f"rm {self.__get_folder_temp_dir_server()}")
        server.exec_command(f"rm {self.__get_folder_temp_dir_server_2()}")

        server.close()

        file_compress = self.__get_backup_drive().set_oauth_backup_database()

        if (os.path.exists(file_path)):
            os.remove(file_path)

        if (os.path.exists(file_path_2)):
            os.remove(file_path_2)

        if (os.path.exists(file_compress)):
            os.remove(file_compress)

    def set_system_backup(self, await_time: int = 5) -> None:
        #-- first connection: compress backup folder
        server = self.__get_ssh_tunnel_conn()
        self.__set_server_system_backup(server)
        server.close()

        #-- second connection: download compressed file
        server = self.__get_ssh_tunnel_conn()
        file_name, file_path = self.__get_system_backup(server)
        file_temp = self.__get_folder_temp_dir_system_server()

        if file_temp != os.getenv("BACKUP_FOLDER_TARGET_SYSTEM"):
            server.exec_command(f"rm {file_temp}")
            
        server.close()

        self.__get_backup_drive().set_oauth_backup_system(file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
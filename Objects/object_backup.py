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
from Objects import Credentials
from Objects import ServiceAccountCredentials

from Commons import commons_global as globals

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

        self.backup_drive = backup_drive

        self.folder_temp_dir = os.path.join(globals.system.get_root_dir(), 'Backups', 'Database')
        self.folder_temp_dir_server = f'/tmp/{os.getenv("SSH_DB_NAME")}_backup.sql'

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

    def __get_database_backup(self, server: paramiko.SSHClient) -> str:
        file_name = f'{self.__get_backup_name()}.sql'
        file_path = os.path.join(globals.system.get_root_dir(), self.__get_folder_temp_dir(), file_name)

        sftp = server.open_sftp()
        sftp.get(self.__get_folder_temp_dir_server(), file_path)
        sftp.close()

        return file_path
    
    def __get_system_backup(self, server: paramiko.SSHClient) -> str:
        file_name = f'{self.__get_backup_name()}.tar.gz'
        file_path = os.path.join(globals.system.get_root_dir(), self.__get_folder_temp_dir_system(), file_name)

        sftp = server.open_sftp()
        sftp.get(self.__get_folder_temp_dir_system_server(), file_path)
        sftp.close()

        return file_name, file_path

    def __set_server_database_backup(self, server: paramiko.SSHClient) -> None:
        command = f"mysqldump -u {self.__get_db_username()} -p{self.__get_db_password()} {self.__get_db_name()} > {self.__get_folder_temp_dir_server()}"
        stdin, stdout, stderr = server.exec_command(command)
        stdout.channel.recv_exit_status()

    def __set_server_system_backup(self, server: paramiko.SSHClient) -> None:
        compress_command = f"tar -czf {self.__get_folder_temp_dir_system_server()} -C {self.__get_folder_temp_dir_system_server_target()} ."
        stdin, stdout, stderr = server.exec_command(compress_command)
        stdout.channel.recv_exit_status()

    def set_database_backup(self, await_time: int = 5) -> None:
        server = self.__get_ssh_tunnel_conn()

        self.__set_server_database_backup(server)
        time.sleep(await_time)

        file_path = self.__get_database_backup(server)

        server.exec_command(f"rm {self.__get_folder_temp_dir_server()}")
        server.close()

        self.__get_backup_drive().set_backup_sql()
        
        if os.path.exists(file_path):
            os.remove(file_path)

    def set_system_backup(self, await_time: int = 5) -> None:
        server = self.__get_ssh_tunnel_conn()
        print('----- CONNECTED TO HOST SERVER -----')

        self.__set_server_system_backup(server)
        time.sleep(await_time)
        print('----- BACKUP CREATED -----')

        file_name, file_path = self.__get_system_backup(server)
        print('----- BACKUP DOWNLOADED -----')

        file_temp = self.__get_folder_temp_dir_system_server()
        if file_temp != os.getenv("BACKUP_FOLDER_TARGET_SYSTEM"):
            server.exec_command(f"rm {file_temp}")
            
        server.close()

        self.__get_backup_drive().set_backup_system(file_name)
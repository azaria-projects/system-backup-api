from Commons import os
from Commons import load_dotenv
from Commons import object_backup

load_dotenv(override=True)

backup = object_backup.object_backup(
    os.getenv("BACKUP_EMAIL"), 
    os.getenv("BACKUP_FOLDER_ID"), 
    os.getenv("BACKUP_FOLDER_TARGET")
)
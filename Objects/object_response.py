from Objects import datetime

class object_response:
    @staticmethod
    def get_api_response(response: int, message: str) -> dict:
        return {
            "response": response,
            "messsage": message
        }
    
    @staticmethod
    def get_drive_folder_metadata(title: str, mime: str = 'application/vnd.google-apps.folder') -> dict:
        return {
            "title": title,
            "mimeType": mime
        }
    
    @staticmethod
    def get_drive_folder_permission(type: str, value: str, role: str) -> dict:
        return {
            "type": type, 
            "value": value, 
            "role": role 
        }
    
    @staticmethod
    def get_drive_file_format(title: str, folder_parents_id: list) -> dict:
        return {
            'title': title, 
            'parents': folder_parents_id
        }
    
    def get_creds_drive_file_format(title: str, folder_parents_id: list) -> dict:
        return {
            'name': title, 
            'parents': folder_parents_id
        }
    
    @staticmethod
    def get_drive_service_account(
        type: str, 
        project_id: str, 
        private_key_id: str,
        private_key: str, 
        client_email: str,
        client_id: str, 
        auth_uri: str,
        token_uri: str, 
        auth_provider_cert_url: str,
        client_cert_url: str, 
        universe_domain: str
    ) -> dict:
        
        return {
            "type": type,
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": private_key,
            "client_email": client_email,
            "client_id": client_id,
            "auth_uri": auth_uri,
            "token_uri": token_uri,
            "auth_provider_x509_cert_url": auth_provider_cert_url,
            "client_x509_cert_url": client_cert_url,
            "universe_domain": universe_domain
        }
    
    @staticmethod
    def get_oauth_creds(
        token: str, 
        refresh_token: str, 
        token_uri: str,
        client_id: str, 
        client_secret: str,
        scopes: str, 
        universe_domain: str,
        account: str, 
        expiry: datetime,
    ) -> dict:
        
        return {
            "token": token, 
            "refresh_token": refresh_token, 
            "token_uri": token_uri, 
            "client_id": client_id, 
            "client_secret": client_secret, 
            "scopes": [scopes], 
            "universe_domain": universe_domain, 
            "account": account, 
            "expiry": expiry.replace(' ', 'T') + 'Z'
        }
from . import os
from . import dotenv

class commons_system:
    @staticmethod
    def get_root_dir() -> str:
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(curr_dir)
        return parent_dir
    
    @staticmethod
    def set_env(env_path: str, env_variable: str, env_value: str) -> None:
        dotenv.set_key(env_path, env_variable, env_value)
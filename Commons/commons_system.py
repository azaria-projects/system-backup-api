from . import os

class commons_system:
    @staticmethod
    def get_root_dir() -> str:
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(curr_dir)
        return parent_dir
from dotenv import load_dotenv
import os


class GLOBALS:
    def __init__(self):
        load_dotenv()
        self.JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
        self.DB_NAME = os.environ.get("DB_NAME")
        self.DB_USERNAME = os.environ.get("DB_USERNAME")
        self.DB_PASSWORD = os.environ.get("DB_PASSWORD")

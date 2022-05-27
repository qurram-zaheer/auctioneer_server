from dataclasses import dataclass

from custom_exceptions.email_exists import EmailAlreadyExistsException
from database_handler import DatabaseHandler


@dataclass
class User:
    email: str
    password: str
    first_name: str
    last_name: str
    gender: str

    def create_user(self):
        user_dict = {"email": self.email, "password": self.password, "first_name": self.first_name,
                     "last_name": self.last_name, "gender": self.gender}
        db_handler = DatabaseHandler()
        if self.verify_existence(self.email, db_handler):
            raise EmailAlreadyExistsException()
        uid = db_handler.add_record(user_dict, "users")
        db_handler.close()
        return uid

    @staticmethod
    def get_user(email):
        db_handler = DatabaseHandler()
        condition = {"email": email}
        record = db_handler.get_single_record(condition, "users")
        db_handler.close()
        return record

    @staticmethod
    def verify_existence(email, db_handler):
        return False if db_handler.get_single_record({"email": email}, "users") is None else True

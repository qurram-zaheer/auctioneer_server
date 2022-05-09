import pymongo
from dotenv import load_dotenv
from GLOBALS import GLOBALS
from bson.json_util import dumps


class DatabaseHandler:
    def __init__(self):
        env_vars = GLOBALS()
        self.client = pymongo.MongoClient(
            f"mongodb+srv://{env_vars.DB_USERNAME}:{env_vars.DB_PASSWORD}@cluster0.4eu2v.mongodb.net/{env_vars.DB_NAME}"
            f"?retryWrites=true&w=majority")
        self.db = self.client[env_vars.DB_NAME]

    def get_all_records(self, collection_name):
        cursor = self.db[collection_name].find()
        return list(cursor)

    def get_single_record(self, condition, collection_name):
        cursor = self.db[collection_name].find_one(condition)
        return cursor

    def get_multiple_records(self, condition, collection_name):
        cursor = self.db[collection_name].find(condition)
        return list(cursor)

    def add_record(self, record, collection_name):
        added_id = self.db[collection_name].insert_one(record)
        return added_id

    def close(self):
        self.client.close()

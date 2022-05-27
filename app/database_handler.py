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
        cleaned_list = []
        for item in list(cursor):
            item["_id"] = str(item["_id"])
            cleaned_list.append(item)
        return cleaned_list

    def get_single_record(self, condition, collection_name):
        cursor = self.db[collection_name].find_one(condition)
        return cursor

    def get_multiple_records(self, condition, collection_name):
        cursor = self.db[collection_name].find(condition)
        return list(cursor)

    def add_record(self, record, collection_name):
        added_id = self.db[collection_name].insert_one(record).inserted_id
        return str(added_id)

    def close(self):
        self.client.close()

    def push(self, item, field, collection_name, condition):
        return self.db[collection_name].update_one(condition, {"$push": {field: item}}).acknowledged

    def set(self, item, field, collection_name, condition):
        return self.db[collection_name].update_one(condition, {"$set": {field: item}}).acknowledged
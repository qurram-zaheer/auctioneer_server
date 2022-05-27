from dataclasses import dataclass

from database_handler import DatabaseHandler
from bson.objectid import ObjectId
from datetime import datetime


@dataclass
class Listing:
    name: str
    subtitle: str
    desc: str
    specs: str
    features: list
    cost: int
    max_cost: int
    image: str

    def create_listing(self):
        parsed_specs = self.specs.split(",")
        specs_dict = {}
        for s in parsed_specs:
            vals = s.split(":")
            specs_dict[vals[0]] = vals[1]
        listing_dict = {"name": self.name, "subtitle": self.subtitle, "desc": self.desc,
                        "specs": specs_dict, "features": self.features, "max_cost": self.max_cost, "image": self.image,
                        "timestamp": datetime.timestamp(datetime.now()), "cost": self.cost, "bids": [],
                        "status": "open",
                        "sold_to": None}
        db_handler = DatabaseHandler()
        _id = db_handler.add_record(listing_dict, "listings")
        db_handler.close()
        return _id

    @staticmethod
    def get_listing(required_id):
        db_handler = DatabaseHandler()
        condition = {"_id": ObjectId(required_id)}
        record = db_handler.get_single_record(condition, "listings")
        record["_id"] = str(record["_id"])
        db_handler.close()
        return record

    @staticmethod
    def get_all_listings():
        db_handler = DatabaseHandler()
        records = db_handler.get_all_records("listings")
        ret_recs = []
        for r in records:
            ts = r['timestamp']
            td = datetime.now() - datetime.fromtimestamp(ts)
            hours = td.days * 24 + td.seconds / 3600
            if hours < 4:
                r['isNew'] = True
            ret_recs.append(r)
        db_handler.close()
        return ret_recs

    @staticmethod
    def add_bid(listing_id, bid_obj):
        condition = {"_id": ObjectId(listing_id)}
        db_handler = DatabaseHandler()
        ack1 = db_handler.push(bid_obj, "bids", "listings", condition)
        ack2 = db_handler.set(bid_obj['amount'], "cost", "listings", condition)
        return ack1 and ack2

    @staticmethod
    def sell_listing(user_id, listing_id):
        db_handler = DatabaseHandler()
        condition = {"_id": ObjectId(listing_id)}
        ack1 = db_handler.set("sold", "status", "listings", condition)
        ack2 = db_handler.set(user_id, "sold_to", "listings", condition)
        return ack1 and ack2

    @staticmethod
    def get_user_listings(user_id):
        db_handler = DatabaseHandler()
        print(user_id)
        condition = {"bids.user": user_id}
        records = db_handler.get_multiple_records(condition, "listings")
        cleaned_records = []
        for r in records:
            r["_id"] = str(r["_id"])
            cleaned_records.append(r)
        print(cleaned_records)
        return cleaned_records

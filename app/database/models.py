from .db import db
import datetime
from bson import json_util


class Pond(db.Document):
    name = db.StringField(required=True)
    location = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.datetime.utcnow)


class FeedType(db.Document):
    name = db.StringField(required=True)
    desc = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.datetime.utcnow)


class FeedHistory(db.Document):
    pond_id = db.ReferenceField(Pond, required=True)
    feed_type_id = db.ReferenceField(FeedType, required=True)
    feed_dose = db.IntField(required=True)
    feed_desc = db.StringField(default="")
    feed_history_time = db.DateTimeField(default=datetime.datetime.utcnow)
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.datetime.utcnow)

    # def to_json(self):
    #     data = self.to_mongo()  # get the pymongo representation of the document
    #     data["pond"] = {
    #         "_id": self.pond_id.id,
    #         "name": self.pond_id.name,
    #         "location": self.pond_id.location
    #     }
    #     data["type_feed"] = {
    #         "_id": self.type_feed_id.id,
    #         "name": self.type_feed_id.name,
    #         "desc": self.type_feed_id.desc
    #     }
    #     return json_util.dumps(data)

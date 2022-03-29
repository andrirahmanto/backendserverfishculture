from .db import db
import datetime
from bson import json_util


class Pond(db.Document):
    name = db.StringField(required=True)
    location = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.datetime.utcnow)


class TypeFeed(db.Document):
    name = db.StringField(required=True)
    desc = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.datetime.utcnow)


class LogFeeding(db.Document):
    pond_id = db.ReferenceField(Pond, required=True)
    type_feed_id = db.ReferenceField(TypeFeed, required=True)
    dose_feed = db.IntField(required=True)
    desc_feed = db.StringField(default="")
    time_feeding = db.DateTimeField(default=datetime.datetime.utcnow)
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

from .db import db
import datetime
from bson import json_util


class Pond(db.Document):
    id_int = db.SequenceField(required=True)
    alias = db.StringField(required=True)
    location = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class FeedType(db.Document):
    name = db.StringField(required=True)
    feed_type = db.StringField(required=True)
    protein = db.IntField(required=True)
    carbohydrate = db.IntField(required=True)
    desc = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class FeedHistory(db.Document):
    pond_id = db.ReferenceField(Pond, required=True)
    feed_type_id = db.ReferenceField(FeedType, required=True)
    feed_dose = db.IntField(required=True)
    feed_history_time = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

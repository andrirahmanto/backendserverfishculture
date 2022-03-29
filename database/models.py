from .db import db
import datetime


class LogFeeding(db.Document):
    pond_id = db.StringField(required=True)
    type_feed_id = db.StringField(required=True)
    dose_feed = db.IntField(required=True)
    desc_feed = db.StringField(default="")
    time_feeding = db.DateTimeField(default=datetime.datetime.utcnow)
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.datetime.utcnow)


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

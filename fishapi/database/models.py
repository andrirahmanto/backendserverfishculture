from .db import db
import datetime
from bson import json_util


class Pond(db.Document):
    id_int = db.SequenceField(required=True)
    alias = db.StringField(required=True)
    location = db.StringField(required=True)
    shape = db.StringField(required=True)
    material = db.StringField(required=True)
    length = db.FloatField(required=True, default=0)
    width = db.FloatField(required=True, default=0)
    diameter = db.FloatField(required=True, default=0)
    height = db.FloatField(required=True, default=0)
    image_name = db.StringField(required=True, default='default.jpg')
    isActive = db.BooleanField(required=True, default=False)
    build_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class Activation(db.Document):
    fish = db.ListField(required=True)
    water_preparation = db.BooleanField(required=True, default=False)
    water_level = db.FloatField(required=True, default=0)
    activated_at = db.DateTimeField(default=datetime.datetime.now)


class WaterPreparation(db.Document):
    activation_id = db.ReferenceField(Activation, required=True)
    carbohydrate = db.IntField(required=True)
    carbohydrate_type = db.StringField(required=True)
    salt = db.IntField(required=True)
    calcium = db.IntField(required=True)


class Diactivation(db.Document):
    total_fish_harvested = db.IntField(required=True)
    total_weight_harvested = db.FloatField(required=True)
    deactivated_at = db.DateTimeField(default=datetime.datetime.now)


class PondStatus(db.Document):
    pond_id = db.ReferenceField(Pond, required=True)
    activation_id = db.ReferenceField(Activation, required=True)
    diactivation_id = db.ReferenceField(Diactivation, required=True)
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

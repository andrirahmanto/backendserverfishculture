from .db import db
import datetime
from bson import json_util
from mongoengine import connect, disconnect

_meta = {
    'db_alias' : 'prod_connection',
}
class Farm(db.Document):
    meta = _meta
    farm_name = db.StringField(required=True)
    address = db.StringField(required=True)
    breeder = db.StringField(required=True)
    coordinate = db.StringField()


class Breeder(db.Document):
    meta = _meta
    farm_id = db.ReferenceField(Farm, required=True)
    username = db.StringField(required=True)
    password = db.StringField(required=True)
    name = db.StringField(required=True)
    nik = db.StringField(required=True)
    phone = db.StringField(required=True)


class Pond(db.Document):
    meta = _meta
    shape_option = ("bundar", "persegi")

    farm_id = db.ReferenceField(Farm, required=True)
    id_int = db.SequenceField(required=True)
    alias = db.StringField(required=True)
    location = db.StringField(required=True)
    shape = db.StringField(required=True, choices=shape_option)
    material = db.StringField(required=True)
    length = db.FloatField(required=True, default=0)
    width = db.FloatField(required=True, default=0)
    status = db.StringField(required=True)
    diameter = db.FloatField(required=True, default=0)
    height = db.FloatField(required=True, default=0)
    image_name = db.StringField(required=True, default='default.jpg')
    isActive = db.BooleanField(required=True, default=False)
    pondPhDesc = db.StringField(default="Belum Diukur")
    pondPh = db.FloatField(default=None)
    pondDoDesc = db.StringField(default="Belum Diukur")
    pondDo = db.FloatField(default=None)
    pondTemp = db.FloatField(default=None)
    build_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class PondActivation(db.Document):
    meta = _meta
    id_int = db.IntField(required=True)
    pond_id = db.ReferenceField(Pond, required=True)
    isFinish = db.BooleanField(required=True, default=False)
    isWaterPreparation = db.BooleanField(required=True, default=False)
    water_level = db.FloatField(required=True, default=0)
    total_fish_harvested = db.IntField(required=True, default=0)
    total_weight_harvested = db.FloatField(required=True, default=0)
    # fish_harvested = db.ArrayField(default=None)
    activated_at = db.DateTimeField(default=datetime.datetime.now)
    deactivated_at = db.DateTimeField(default=None)
    deactivated_description = db.StringField(default=None)
    amount_normal_fish = db.IntField(default=None)
    amount_oversize_fish = db.IntField(default=None)
    amount_undersize_fish = db.IntField(default=None)
    sample_amount = db.IntField(default=None)
    sample_weight = db.FloatField(default=None)
    sample_long = db.FloatField(default=None)
    constanta_oversize = db.FloatField(required=True, default=1.3)
    constanta_undersize = db.FloatField(required=True, default=0.7)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class WaterPreparation(db.Document):
    meta = _meta
    carbohydrate_type_option = ("gula", "molase", "terigu", "tapioka")

    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    carbohydrate = db.IntField(required=True)
    carbohydrate_type = db.StringField(
        required=True, choices=carbohydrate_type_option)
    salt = db.IntField(required=True)
    calcium = db.IntField(required=True)


class FeedType(db.Document):
    meta = _meta
    feed_type_option = ("pelet", "alternatif")

    name = db.StringField(required=True)
    feed_type = db.StringField(required=True, choices=feed_type_option)
    protein = db.IntField(required=True)
    carbohydrate = db.IntField(required=True)
    desc = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class FeedHistory(db.Document):
    meta = _meta
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    feed_type_id = db.ReferenceField(FeedType, required=True)
    feed_dose = db.FloatField(required=True)
    feed_history_time = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class FishDeath(db.Document):
    meta = _meta
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    image_name = db.StringField(required=True)
    diagnosis = db.StringField(default=datetime.datetime.now)
    death_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class FishTransfer(db.Document):
    meta = _meta
    transfer_method_option = ("basah", "kering")
    transfer_type_option = ("", "oversized_transfer", "undersized_transfer", "maintain_transfer")

    origin_pond_id = db.ReferenceField(Pond, required=True)
    destination_pond_id = db.ReferenceField(Pond, required=True)
    origin_activation_id = db.ReferenceField(PondActivation, required=True)
    destination_activation_id = db.ReferenceField(
        PondActivation, required=True)
    # fish_grading_id = db.ObjectIdField(required=True, default=None)
    transfer_type = db.StringField(choices=transfer_type_option, default="")
    transfer_method = db.StringField(
        required=True, choices=transfer_method_option)
    sample_weight = db.FloatField(default=0)
    sample_long = db.FloatField(default=0)
    transfer_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class FishLog(db.Document):
    meta = _meta
    fish_type_option = ("nila hitam", "nila merah", "lele", "patin", "mas")

    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ObjectIdField(required=False, default=None)
    fish_death_id = db.ObjectIdField(required=False, default=None)
    fish_transfer_id = db.ObjectIdField(required=False, default=None)
    type_log = db.StringField(required=True)
    fish_type = db.StringField(required=True, choices=fish_type_option)
    fish_amount = db.IntField(required=True)
    fish_total_weight = db.FloatField(default=None)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class FishGrading(db.Document):
    meta = _meta
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    isOversizeTransferred = db.BooleanField(required=True, default=False)
    isUndersizeTransferred = db.BooleanField(required=True, default=False)
    fish_type = db.StringField(required=True)
    sampling_amount = db.IntField(required=True)
    avg_fish_weight = db.FloatField(required=True)
    avg_fish_long = db.FloatField(default=None)
    amount_normal_fish = db.IntField(default=None)
    amount_oversize_fish = db.IntField(default=None)
    amount_undersize_fish = db.IntField(default=None)
    grading_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class DailyWaterQuality(db.Document):
    meta = _meta
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    ph = db.FloatField(required=True)
    do = db.FloatField(required=True)
    temperature = db.FloatField(required=True)
    week = db.IntField(defauit=None)
    dailywater_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class WeeklyWaterQuality(db.Document):
    meta = _meta
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    floc = db.FloatField(required=True)
    nitrite = db.FloatField(Default=None)
    nitrate = db.FloatField(Default=None)
    ammonia = db.FloatField(Default=None)
    hardness = db.FloatField(Default=None)
    week = db.IntField(Default=None)
    weeklywater_at= db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class PondTreatment(db.Document):
    meta = _meta
    treatment_type_option = ("ringan", "berat", "pergantian air")
    carbohydrate_type_option = ("", "gula", "molase", "terigu", "tapioka")

    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    treatment_type = db.StringField(
        required=True, choices=treatment_type_option)
    water_change = db.IntField()
    salt = db.FloatField()
    probiotic_culture = db.FloatField()
    carbohydrate = db.FloatField()
    carbohydrate_type = db.StringField(
        required=True, choices=carbohydrate_type_option, default="")
    calcium = db.FloatField(default=0)
    description = db.StringField(default="")
    treatment_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class OptionTable(db.Document):
    meta = _meta
    type = db.StringField(required=True)
    option = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class Logging(db.Document):
    meta = _meta
    farm_id = db.ReferenceField(Farm)
    breeder_id = db.ReferenceField(Breeder)
    farm_name = db.StringField()
    breeder_name = db.StringField()
    start_at = db.DateTimeField()
    end_at = db.DateTimeField()
    duration = db.StringField()
    feature_name = db.StringField()

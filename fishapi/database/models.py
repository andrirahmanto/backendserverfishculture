from mongoengine import *
import datetime
from bson import json_util

db = connect(alias='v1connection')

class Pond(Document):
    shape_option = ("bundar", "persegi")

    id_int = SequenceField(required=True)
    alias = StringField(required=True)
    location = StringField(required=True)
    shape = StringField(required=True, choices=shape_option)
    material = StringField(required=True)
    length = FloatField(required=True, default=0)
    width = FloatField(required=True, default=0)
    diameter = FloatField(required=True, default=0)
    height = FloatField(required=True, default=0)
    image_name = StringField(required=True, default='default.jpg')
    isActive = BooleanField(required=True, default=False)
    build_at = DateTimeField(default=datetime.datetime.now)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


class PondActivation(Document):
    id_int = IntField(required=True)
    pond_id = ReferenceField(Pond, required=True)
    isFinish = BooleanField(required=True, default=False)
    isWaterPreparation = BooleanField(required=True, default=False)
    water_level = FloatField(required=True, default=0)
    total_fish_harvested = IntField(required=True, default=0)
    total_weight_harvested = IntField(required=True, default=0)
    activated_at = DateTimeField(default=datetime.datetime.now)
    deactivated_at = DateTimeField(default=None)
    deactivated_description = StringField(default=None)
    constanta_oversize = FloatField(required=True, default=1.3)
    constanta_undersize = FloatField(required=True, default=0.7)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


class WaterPreparation(Document):
    carbohydrate_type_option = ("gula", "molase", "terigu", "tapioka")

    pond_activation_id = ReferenceField(PondActivation, required=True)
    carbohydrate = IntField(required=True)
    carbohydrate_type = StringField(
        required=True, choices=carbohydrate_type_option)
    salt = IntField(required=True)
    calcium = IntField(required=True)


class FeedType(Document):
    feed_type_option = ("pelet", "sayuran")

    name = StringField(required=True)
    feed_type = StringField(required=True, choices=feed_type_option)
    protein = IntField(required=True)
    carbohydrate = IntField(required=True)
    desc = StringField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


class FeedHistory(Document):
    pond_id = ReferenceField(Pond, required=True)
    pond_activation_id = ReferenceField(PondActivation, required=True)
    feed_type_id = ReferenceField(FeedType, required=True)
    feed_dose = IntField(required=True)
    feed_history_time = DateTimeField(default=datetime.datetime.now)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


class FishDeath(Document):
    pond_id = ReferenceField(Pond, required=True)
    pond_activation_id = ReferenceField(PondActivation, required=True)
    image_name = StringField(required=True)
    diagnosis = StringField(default=datetime.datetime.now)
    death_at = DateTimeField(default=datetime.datetime.now)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


class FishTransfer(Document):
    transfer_method_option = ("basah", "kering")
    transfer_type_option = ("", "oversized_transfer", "undersized_transfer")

    origin_pond_id = ReferenceField(Pond, required=True)
    destination_pond_id = ReferenceField(Pond, required=True)
    origin_activation_id = ReferenceField(PondActivation, required=True)
    destination_activation_id = ReferenceField(
        PondActivation, required=True)
    fish_grading_id = ObjectIdField(required=True, default=None)
    transfer_type = StringField(choices=transfer_type_option, default="")
    transfer_method = StringField(
        required=True, choices=transfer_method_option)
    sample_weight = IntField(required=True)
    sample_long = IntField(default=None)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


class FishLog(Document):
    fish_type_option = ("nila hitam", "nila merah", "lele", "patin", "mas")

    pond_id = ReferenceField(Pond, required=True)
    pond_activation_id = ObjectIdField(required=False, default=None)
    fish_death_id = ObjectIdField(required=False, default=None)
    fish_transfer_id = ObjectIdField(required=False, default=None)
    type_log = StringField(required=True)
    fish_type = StringField(required=True, choices=fish_type_option)
    fish_amount = IntField(required=True)
    fish_total_weight = IntField(default=None)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


class FishGrading(Document):
    pond_id = ReferenceField(Pond, required=True)
    pond_activation_id = ReferenceField(PondActivation, required=True)
    isOversizeTransferred = BooleanField(required=True, default=False)
    isUndersizeTransferred = BooleanField(required=True, default=False)
    fish_type = StringField(required=True)
    sampling_amount = IntField(required=True)
    avg_fish_weight = FloatField(required=True)
    avg_fish_long = FloatField(required=True)
    amount_normal_fish = IntField(required=True)
    amount_oversize_fish = IntField(required=True)
    amount_undersize_fish = IntField(required=True)
    grading_at = DateTimeField(default=datetime.datetime.now)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


class DailyWaterQuality(Document):
    pond_id = ReferenceField(Pond, required=True)
    pond_activation_id = ReferenceField(PondActivation, required=True)
    ph = IntField(required=True)
    do = FloatField(required=True)
    temperature = IntField(required=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


class WeeklyWaterQuality(Document):
    floc_option = ('0-10', '11-30', '31-50', '51-100', '101-300', '>300')
    nitrite_option = (0, 1, 5, 10, 20, 40, 80)
    nitrate_option = (0, 10, 25, 50, 100, 250, 500)
    ammonia_option = (0, 0.25, 1.5, 3, 5)
    hardness_option = (0, 25, 50, 125, 250, 425)

    pond_id = ReferenceField(Pond, required=True)
    pond_activation_id = ReferenceField(PondActivation, required=True)
    floc = StringField(required=True, choices=floc_option)
    nitrite = IntField(required=True, choices=nitrite_option)
    nitrate = IntField(required=True, choices=nitrate_option)
    ammonia = FloatField(required=True, choices=ammonia_option)
    hardness = IntField(required=True, choices=hardness_option)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


class PondTreatment(Document):
    treatment_type_option = ("ringan", "karantina", "pergantian air")
    carbohydrate_type_option = ("", "gula", "molase", "terigu", "tapioka")

    pond_id = ReferenceField(Pond, required=True)
    pond_activation_id = ReferenceField(PondActivation, required=True)
    treatment_type = StringField(
        required=True, choices=treatment_type_option)
    water_change = IntField()
    salt = IntField()
    probiotic_culture = IntField()
    carbohydrate = IntField()
    carbohydrate_type = StringField(
        required=True, choices=carbohydrate_type_option, default="")
    description = StringField(default="")
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


class OptionTable(Document):
    type = StringField(required=True)
    option = StringField(required=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

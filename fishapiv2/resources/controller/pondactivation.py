from bson import ObjectId
from flask import Response, jsonify, request, current_app
from fishapiv2.database.models import *
from flask_restful import Resource
from fishapiv2.database.db import db
from fishapiv2.resources.helper import getYearToday
import datetime
import json
from bson.json_util import dumps


class PondsStatusApi(Resource):
    def get(self):
        pipline = [
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                    ]}}},
                    {'$lookup': {
                        'from': 'water_preparation',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id', '$$pond_activation_id']}}},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                        'as': 'water_preparation'
                    }},
                    {"$addFields": {
                        "water_preparation": {"$first": "$water_preparation"}
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_type_id": 0,
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'pond_activation_list'
            }},
            {"$addFields": {
                "total_activation": {"$size": "$pond_activation_list"},
            }},
            {"$project": {
                "location": 0,
                "shape": 0,
                "material": 0,
                "length": 0,
                "width": 0,
                "diameter": 0,
                "height": 0,
                "image_name": 0,
                "pond_activation_list": 0,
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipline)
        response = list(ponds)
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)


class PondStatusApi(Resource):
    def get(self, pond_id):
        pond_objects = Pond.objects.get(id=pond_id)
        pipline = [
            {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': pond_id}]}}},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                    ]}}},
                    {"$sort": {"activated_at": -1}},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'activation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"},
                                "fish_total_weight": {"$sum": "$fish_total_weight"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_stock'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$ne': ['$type_log', 'deactivation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_live'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'death']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_death'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'deactivation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"},
                                "fish_total_weight": {"$sum": "$fish_total_weight"},
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_harvested'
                    }},
                    {'$lookup': {
                        'from': 'feed_history',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                ]}
                            }},
                        ],
                        'as': 'feed_history'
                    }},
                    {'$lookup': {
                        'from': 'water_preparation',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id', '$$pond_activation_id']}}},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                        'as': 'water_preparation'
                    }},
                    {"$addFields": {
                        "water_preparation": {"$first": "$water_preparation"},
                        "total_fish": {"$sum": "$fish_live.fish_amount"},
                        "survival_rate": {"$cond": [
                            {"$eq": [{"$sum": "$fish_stock.fish_amount"}, 0]},
                            0,
                            {"$multiply": [{"$divide": [{"$sum": "$fish_live.fish_amount"}, {
                                "$sum": "$fish_stock.fish_amount"}]}, 100]}
                        ]},
                        "weight_growth": {"$subtract": [{"$sum": "$fish_harvested.fish_total_weight"}, {"$sum": "$fish_stock.fish_total_weight"}]},
                        "total_dose": {"$sum": "$feed_history.feed_dose"},
                        # "fcr": {"$sum": {"$divide": [{"$sum": "$fish_live.fish_amount"}, {"$sum": "$fish_stock.fish_amount"}]}},
                    }},
                    {"$addFields": {
                        "fcr": {"$cond": [
                            {"$eq": [{"$sum": "$total_dose"}, 0]},
                            0,
                            {"$sum": {"$divide": [
                                "$weight_growth", "$total_dose"]}}
                        ]},
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_history": 0,
                        "feed_type_id": 0,
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'pond_activation_list'
            }},
            {"$addFields": {
                "total_activation": {"$size": "$pond_activation_list"},
                "pond_activation_list": '$pond_activation_list',

            }},
            {"$project": {
                "location": 0,
                "shape": 0,
                "material": 0,
                "length": 0,
                "width": 0,
                "diameter": 0,
                "height": 0,
                "image_name": 0,
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipline)
        ponds = list(ponds)
        ponds = dict(ponds[0])
        response = json.dumps(ponds, default=str)
        return Response(response, mimetype="application/json", status=200)


class PondActivationDetailApi(Resource):
    def get(self,id, pond):
        # log = FishLog.objects(pond_activation_id=id, type_log="deactivation").first()
        # response = json.dumps(ponds, default=str)
        activation = PondActivation.objects(id=id).first()
        pond_id = ObjectId(pond)
        # pond = Pond.objects(id=pond).first()
        pipline = [
            
            {'$match': {'$expr': {'$eq': ['$_id', pond_id]}}},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                    ]}}},
                    {"$sort": {"activated_at": -1}},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'activation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"},
                                "fish_total_weight": {"$sum": "$fish_total_weight"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_stock'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$ne': ['$type_log', 'deactivation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_live'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'death']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_death'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'deactivation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"},
                                "fish_total_weight": {"$sum": "$fish_total_weight"},
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_harvested'
                    }},
                    {'$lookup': {
                        'from': 'feed_history',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                ]}
                            }},
                        ],
                        'as': 'feed_history'
                    }},
                    {'$lookup': {
                        'from': 'water_preparation',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id', '$$pond_activation_id']}}},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                        'as': 'water_preparation'
                    }},
                    {"$addFields": {
                        "water_preparation": {"$first": "$water_preparation"},
                        "total_fish": {"$sum": "$fish_live.fish_amount"},
                        "survival_rate": {"$cond": [
                            {"$eq": [{"$sum": "$fish_stock.fish_amount"}, 0]},
                            0,
                            {"$multiply": [{"$divide": [{"$sum": "$fish_live.fish_amount"}, {
                                "$sum": "$fish_stock.fish_amount"}]}, 100]}
                        ]},
                        "weight_growth": {"$subtract": [{"$sum": "$fish_harvested.fish_total_weight"}, {"$sum": "$fish_stock.fish_total_weight"}]},
                        "total_dose": {"$sum": "$feed_history.feed_dose"},
                        # "fcr": {"$sum": {"$divide": [{"$sum": "$fish_live.fish_amount"}, {"$sum": "$fish_stock.fish_amount"}]}},
                    }},
                    {"$addFields": {
                        "fcr": {"$cond": [
                            {"$eq": [{"$sum": "$total_dose"}, 0]},
                            0,
                            {"$sum": {"$divide": [
                                "$weight_growth", "$total_dose"]}}
                        ]},
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_history": 0,
                        "feed_type_id": 0,
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'pond_activation_list'
            }},
            {"$addFields": {
                "total_activation": {"$size": "$pond_activation_list"},
                "pond_activation_list": '$pond_activation_list',

            }},
            {"$project": {
                "location": 0,
                "shape": 0,
                "material": 0,
                "length": 0,
                "width": 0,
                "diameter": 0,
                "height": 0,
                "image_name": 0,
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipline)
        ponds = list(ponds)
        activ = None
        for acti in ponds[0]["pond_activation_list"]:
            # activ = acti["_id"]
            if str(acti["_id"]) == id:
                activ = acti
        if activ == None:
            activ =0
        response =  {
            "id": activation.id,
            "pond_id": pond,
            # "pond_id": activation.pond_id,
            "is_finish": activation.isFinish,
            "water_level": activation.water_level,
            "total_fish_harvested": activation.total_fish_harvested,
            "total_weight_harvested": activation.total_weight_harvested,
            "activation_at": activation.activated_at,
            "deactivation_at": activation.deactivated_at,
            "deactivation_description": activation.deactivated_description,
            "fish_activated": activ["fish_stock"],
            "fish_alive": activ["fish_live"],
            "fish_harvested": activ["fish_harvested"],
            "fish_death": activ["fish_death"]
        }
        response = json.dumps(response, default=str)
        # response = jsonify(activation.__dict__)
        return Response(response, mimetype="application/json", status=200)

class PondActivationApi(Resource):
    def post(self, pond_id):
        pond = Pond.objects.get(id=pond_id)
        pipeline_year = {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', {'$toObjectId': pond_id}]},
                        {'$eq': [{'$dateToString': {
                            'format': "%Y", 'date': "$created_at"}}, getYearToday()]},
        ]
        }}}
        list_pond_year = PondActivation.objects.aggregate(pipeline_year)
        list_pond_year = list(list_pond_year)
        id_int = len(list_pond_year) + 1
        if pond.isActive == True:
            response = {"message": "status pond is already active"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        fishes = request.form.get("fish", "[]")
        fishes = json.loads(fishes)
        if len(fishes) < 1:
            response = {"message": "There is no fish"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        isWaterPreparation = request.form.get("isWaterPreparation", False)
        # fish_harvested = request.form.get("fish_harvested", None)
        if isWaterPreparation == "true":
            isWaterPreparation = True
        else:
            isWaterPreparation = False
        water_level = request.form.get("water_level", None)
        activated_at = request.form.get(
            "activated_at", datetime.datetime.now())
        pond_activation_data = {
            "id_int": id_int,
            "pond_id": pond_id,
            "isFinish": False,
            "isWaterPreparation": isWaterPreparation,
            "water_level": water_level,
            "activated_at": activated_at
        }
        pondActivation = PondActivation(**pond_activation_data).save(using=current_app.config['CONNECTION'])
        pondActivation_id = pondActivation.id
        if isWaterPreparation == True:
            carbohydrate = request.form.get("carbohydrate", None)
            carbohydrate_type = request.form.get("carbohydrate_type", None)
            salt = request.form.get("salt", None)
            calcium = request.form.get("calcium", None)
            water_preparation_data = {
                "pond_activation_id": pondActivation_id,
                "carbohydrate": carbohydrate,
                "carbohydrate_type": carbohydrate_type,
                "salt": salt,
                "calcium": calcium,
            }
            water_preparation = WaterPreparation(
                **water_preparation_data).save(using=current_app.config['CONNECTION'])
        pond.update(**{"isActive": True,
        "status": "Aktif",  "pondDoDesc": "Belum Diukur", "pondPhDesc": "Belum Diukur", "pondPh": None, "pondDo": None, "pondTemp": None})
        for fish in fishes:
            # save fish log
            data = {
                "pond_id": pond_id,
                "pond_activation_id": pondActivation_id,
                "type_log": "activation",
                "fish_type": fish['type'],
                "fish_amount": fish['amount'],
                "fish_total_weight": fish['weight']
            }
            fishlog = FishLog(**data).save(using=current_app.config['CONNECTION'])
        response = {"message": "success to activation pond"}
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)


class PondDeactivationApi(Resource):
    def post(self, pond_id):
        pond = Pond.objects.get(id=pond_id)
        if pond.isActive == False:
            response = {"message": "status pond is already not active"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        # get last pond_activation
        pond_activation = PondActivation.objects(
            pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
        fishes = request.form.get("fish", "[]")
        fishes = json.loads(fishes)
        total_fish_harvested = request.form.get("total_fish_harvested", None)
        amount_undersize = request.form.get("amount_undersize", None)
        amount_oversize = request.form.get("amount_oversize", None)
        amount_normal = request.form.get("amount_normal", None)
        sample_weight = request.form.get("sample_weight", None)
        sample_amount = request.form.get("sample_amount", None)
        sample_long = request.form.get("sample_long", None)
        total_weight_harvested = request.form.get("total_weight_harvested", None)
        # fish_harvested = request.form.get("fish_harvested", None)
        for fish in fishes:
            # save fish log
            data = {
                "pond_id": pond_id,
                "pond_activation_id": pond_activation.id,
                "type_log": "deactivation",
                "fish_type": fish['type'],
                "fish_amount": fish['amount'],
                "fish_total_weight": fish['weight'],
            }
            # total_fish_harvested += fish['amount']
            # total_weight_harvested += fish['weight']
            fishlog = FishLog(**data).save(using=current_app.config['CONNECTION'])
            print(data)
        print(total_fish_harvested)
        print(total_weight_harvested)
        # get args form data
        # update pond_activation
        pond_deactivation_data = {
            "isFinish": True,
            "total_fish_harvested": total_fish_harvested,
            "total_weight_harvested": total_weight_harvested,
            "deactivated_at": request.form.get("deactivated_at", datetime.datetime.now()),
            "deactivated_description": "Normal",
            "amount_undersize_fish":amount_undersize,
            "amount_oversize_fish":amount_oversize,
            "amount_normal_fish":amount_normal,
            "sample_amount":sample_amount,
            "sample_long":sample_long,
            "sample_weight": sample_weight
        }
        pond_activation.update(**pond_deactivation_data)
        # update pond isActive
        pond.update(**{"isActive": False,"status": "Panen"})
        response = {"message": "success to deactivation pond"}
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)

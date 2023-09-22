from bson import ObjectId
from flask import Response, jsonify, request, current_app
from fishapiv2.database.models import *
from flask_restful import Resource, reqparse
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
                    # {'$lookup': {
                    #     'from': 'fish_log',
                    #     'let': {"pond_activation_id": "$_id"},
                    #     'pipeline': [
                    #         {'$match': {
                    #             '$expr': {'$and': [
                    #                 {'$eq': ['$pond_activation_id',
                    #                  '$$pond_activation_id']},
                    #                 {'$eq': ['$type_log', 'activation']},
                    #             ]}
                    #         }},
                    #         {"$project": {
                    #             "created_at": 0,
                    #             "updated_at": 0,
                    #         }},
                    #         {"$group": {
                    #             "_id": "$fish_type",
                    #             "fish_type": {"$first": "$fish_type"},
                    #             "fish_amount": {"$sum": "$fish_amount"},
                    #             "fish_total_weight": {"$sum": "$fish_total_weight"}
                    #         }},
                    #         {"$sort": {"fish_type": -1}},
                    #         {"$project": {
                    #             "_id": 0,
                    #         }},
                    #     ],
                    #     'as': 'fish_stock'
                    # }},
                    {'$lookup': {
                        'from': 'fish_grading',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']}
                            }},
                            {"$sort": {"_id": -1}},
                        ],
                        'as': 'list_grading'
                    }},
                    {'$lookup': {
                        'from': 'fish_harvested',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']}
                            }},
                            {"$sort": {"_id": -1}},
                        ],
                        'as': 'list_fish_harvested'
                    }},
                    {"$addFields": {
                        "first_fish_harvested": {"$first": "$list_fish_harvested"},
                    }},
                    {"$addFields": {
                        "fish_harvested": "$first_fish_harvested.fish",
                        "total_fish_harvested": "$first_fish_harvested.total_fish_harvested",
                        "total_weight_harvested": "$first_fish_harvested.total_weight_harvested"
                    }},
                    {"$project": {
                        "list_fish_harvested": 0,
                        # "first_fish_harvested": 0,
                    }},

                    # {'$lookup': {
                    #     'from': 'fish_log',
                    #     'let': {"pond_activation_id": "$_id"},
                    #     'pipeline': [
                    #         {'$match': {
                    #             '$expr': {'$and': [
                    #                 {'$eq': ['$pond_activation_id',
                    #                          '$$pond_activation_id']},
                    #                 {'$eq': ['$type_log', 'DEATH']},
                    #             ]}
                    #         }},
                    #         {"$group": {
                    #             "_id": "$fish_type",
                    #             "fish_type": {"$first": "$fish_type"},
                    #             "fish_amount": {"$sum": "$fish_amount"}
                    #         }},
                    #         {"$sort": {"fish_type": -1}},
                    #         {"$project": {
                    #             "_id": 0,
                    #         }},
                    #     ],
                    #     'as': 'fish_death'
                    # }},
                    # {'$lookup': {
                    #     'from': 'fish_log',
                    #     'let': {"pond_activation_id": "$_id"},
                    #     'pipeline': [
                    #         {'$match': {
                    #             '$expr': {'$and': [
                    #                 {'$eq': ['$pond_activation_id',
                    #                  '$$pond_activation_id']},
                    #                 {'$eq': ['$type_log', 'deactivation']},
                    #             ]}
                    #         }},
                    #         {"$group": {
                    #             "_id": "$fish_type",
                    #             "fish_type": {"$first": "$fish_type"},
                    #             "fish_amount": {"$sum": "$fish_amount"},
                    #             "fish_total_weight": {"$sum": "$fish_total_weight"},
                    #         }},
                    #         {"$sort": {"fish_type": -1}},
                    #         {"$project": {
                    #             "_id": 0,
                    #         }},
                    #     ],
                    #     'as': 'fish_harvested'
                    # }},
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
                    {"$addFields": {
                        "fish_live": {"$first": "$list_grading.fish"},
                        "fish_death": [],
                        "fish_harvested": [],
                        "fish_stock": [],
                        "fcr": {"$first": "$list_grading.fcr"},
                        "fcr_update": {"$first": "$list_grading.created_at"},
                        "last_feed_dose": {"$first": "$feed_history.created_at"},
                        "feed_dose": {"$sum": "$feed_history.feed_dose"},
                    }},
                    {"$addFields": {
                        "total_fish": {"$sum": "$fish_live.amount"},
                        "survival_rate": {"$cond": [
                            {"$eq": [{"$sum": "$fish_stock.fish_amount"}, 0]},
                            0,
                            {"$multiply": [{"$divide": [{"$sum": "$fish_live.fish_amount"}, {
                                "$sum": "$fish_stock.fish_amount"}]}, 100]}
                        ]},
                        "weight_growth": {"$subtract": [{"$sum": "$fish_harvested.fish_total_weight"}, {"$sum": "$fish_stock.fish_total_weight"}]},
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_history": 0,
                        "feed_type_id": 0,
                        "list_grading": 0,
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
                        'from': 'fish_grading',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']}
                            }},
                            {"$sort": {"_id": -1}},
                        ],
                        'as': 'list_grading'
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
                    {"$addFields": {
                        "last_grading": {"$first": "$list_grading"},
                    }},
                    {"$addFields": {
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

        def _activationValidation(pond_id , args):
            # pond id validation
            if (pond_id == None):
                raise Exception('Pond_id Tidak boleh kosong')
            pond = Pond.objects(id=pond_id).first()
            if (not pond):
                raise Exception('Pond_id Tidak ditemukan')
            if (pond.isActive == True):
                raise Exception('Pond masih dalam masa budidaya')
            # fish validation
            str_fish_list = args['fish']
            fish_list = json.loads(str_fish_list)
            if (len(fish_list)<1):
                raise Exception('list fish harus lebih dari atau sama dengan 1')
            return

        parser = reqparse.RequestParser()
        parser.add_argument('fish', type=str, required=True, location='form')
        parser.add_argument('water_level', type=str, required=True, location='form')
        parser.add_argument('activationType', type=str, default='', location='form')
        parser.add_argument('benihType', type=str, default='', location='form')
        args = parser.parse_args()
        fish = json.loads(args.fish)
        print(args)
        print(fish)
        print(type(fish))
        _activationValidation(pond_id=pond_id, args=args)
        pond = Pond.objects(id=pond_id).first()
        pipeline_year = {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', {'$toObjectId': pond_id}]},
                        {'$eq': [{'$dateToString': {
                            'format': "%Y", 'date': "$created_at"}}, getYearToday()]},
        ]
        }}}
        list_pond_year = PondActivation.objects.aggregate(pipeline_year)
        list_pond_year = list(list_pond_year)
        id_int = len(list_pond_year) + 1
        activated_at = request.form.get(
            "activated_at", datetime.datetime.now())
        pondActivation = PondActivation(
            pond_id = pond,
            isFinish = False,
            activationType = args.activationType,
            benihType = args.benihType,
            water_level = args.water_level,
            activated_at = activated_at,
        )
        #add fish to grading
        fishGrading = FishGrading(
            pond_id = pond,
            pond_activation_id = pondActivation,
            event = pondActivation,
            event_desc = 'ACTIVATION',
            fish = fish,
            fcr = 0,
        )
        fishLog =  FishLog(
            pond_id = pond,
            pond_activation_id = pondActivation,
            event_id = pondActivation,
            type_log = 'ACTIVATION',
            fish = fish,
        )
        pondActivation.save(using=current_app.config['CONNECTION'])
        fishGrading.save(using=current_app.config['CONNECTION'])
        fishLog.save(using=current_app.config['CONNECTION'])
        pond.update(isActive=True)

        response = {"message": "success to activation pond"}
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)


class PondDeactivationApi(Resource):
    def post(self, pond_id):

        def _udpateFishWithNewWeight(fishes, total_fish_harvested, total_weight_harvested):
            newFishes = []
            for fish in fishes:
                fish['amount'] = int(fish['amount'])
                fish['weight'] = float(total_weight_harvested) / int(total_fish_harvested)
                newFishes.append(fish)
            return newFishes

        def _getTotalWeightFromListFishLastGrading(listFish):
                totalWeight = 0
                for fish in listFish:
                    weight = fish['amount']*fish['weight']
                    totalWeight += weight
                return totalWeight
        
        def _getFcr(pond_activation,total_weight_harvested):
            last_grading_activation = FishGrading.objects(pond_activation_id=pond_activation.id).order_by('-grading_at').first()
            date_last_grading_activation = last_grading_activation.grading_at
            date_now = datetime.datetime.now()
            total_feed_dose_before_last_grading = FeedHistory.objects(
                pond_activation_id=pond_activation.id,
                feed_history_time__lt=date_last_grading_activation
            ).sum('feed_dose')
            total_feed_dose_before_now = FeedHistory.objects(
                pond_activation_id=pond_activation.id,
                feed_history_time__lt=date_now
            ).sum('feed_dose')
            diff_feed_dose = total_feed_dose_before_now-total_feed_dose_before_last_grading
            total_fish_weight_last_grading = _getTotalWeightFromListFishLastGrading(list(last_grading_activation.fish))
            total_fish_weight_now = total_weight_harvested
            diff_fish_weight = float(total_fish_weight_now) - total_fish_weight_last_grading
            fcr = diff_feed_dose / diff_fish_weight
            return fcr

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
        sample_weight = request.form.get("sample_weight", None)
        sample_amount = request.form.get("sample_amount", None)
        sample_long = request.form.get("sample_long", None)
        total_weight_harvested = request.form.get("total_weight_harvested", None)
        newFishes = _udpateFishWithNewWeight(fishes,total_fish_harvested,total_weight_harvested)
        fcr = _getFcr(pond_activation=pond_activation,total_weight_harvested=total_weight_harvested)
        # save fish harvested
        fishHarvested = FishHarvested(
            pond_id = pond,
            pond_activation_id = pond_activation,
            fish = fishes,
            fcr = fcr,
            total_weight_harvested = total_weight_harvested,
            total_fish_harvested = total_fish_harvested,
        ).save(using=current_app.config['CONNECTION'])
        # save fish grading
        fish_grading = FishGrading(
            pond_id = pond,
            pond_activation_id = pond_activation,
            event = fishHarvested,
            event_desc = 'DEACTIVATION',
            fish = fishes,
            fcr = fcr,
            sample_amount = total_fish_harvested,
            sample_weight = total_weight_harvested,
            sample_long = sample_long,
        ).save(using=current_app.config['CONNECTION'])
        # update activation
        pond_activation.update(
            isFinish=True,
            deactivated_at = request.form.get("deactivated_at", datetime.datetime.now()),
        )
        # updat pond
        pond.update(
            isActive = False
        )

        response = {"message": "success to deactivation pond"}
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)

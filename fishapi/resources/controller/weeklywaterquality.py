from flask import Response, request
from fishapi.database.models import WeeklyWaterQuality, Pond, PondActivation
from flask_restful import Resource
import datetime
import json


class WeeklyWaterQualitysApi(Resource):
    def get(self):
        try:
            pipeline = [
                {"$sort": {"created_at": -1}},
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                        {"$project": {
                            "_id": 1,
                            "alias": 1,
                            "location": 1,
                            "build_at": 1,
                            "isActive": 1,
                        }}
                    ],
                    'as': 'pond'
                }},
                {'$lookup': {
                    'from': 'pond_activation',
                    'let': {"activationid": "$pond_activation_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$activationid']}}},
                        {"$project": {
                            "_id": 1,
                            "isFinish": 1,
                            "isWaterPreparation": 1,
                            "water_level": 1,
                            "activated_at": 1
                        }}
                    ],
                    'as': 'pond_activation'
                }},
                {"$addFields": {
                    "pond": {"$first": "$pond"},
                    "pond_activation": {"$first": "$pond_activation"},
                    "floc_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {"case": {
                                        "$eq": ["$floc", "0-10"]}, "then": "pembentukan"},
                                    {"case": {
                                        "$eq": ["$floc", "11-30"]}, "then": "normal"},
                                    {"case": {
                                        "$eq": ["$floc", "31-50"]}, "then": "tebal"},
                                    {"case": {
                                        "$eq": ["$floc", "51-100"]}, "then": "abnormal"},
                                    {"case": {
                                        "$eq": ["$floc", "101-300"]}, "then": "berbahaya"},
                                    {"case": {
                                        "$eq": ["$floc", ">300"]}, "then": "deadzone"},
                                ],
                                "default": "normal"
                            }
                    },
                    "nitrite_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {"case": {
                                        "$eq": ["$ammonia", 0]}, "then": "tidak ada"},
                                    {"case": {
                                        "$eq": ["$ammonia", 1]}, "then": "sedikit"},
                                    {"case": {
                                        "$eq": ["$ammonia", 5]}, "then": "aman"},
                                    {"case": {
                                        "$eq": ["$ammonia", 10]}, "then": "pekat"},
                                    {"case": {
                                        "$eq": ["$ammonia", 20]}, "then": "banyak"},
                                    {"case": {
                                        "$eq": ["$ammonia", 40]}, "then": "berbahaya"},
                                    {"case": {
                                        "$eq": ["$ammonia", 80]}, "then": "deadzone"},
                                ],
                                "default": "normal"
                            }
                    },
                    "nitrate_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {"case": {
                                        "$eq": ["$ammonia", 0]}, "then": "tidak ada"},
                                    {"case": {
                                        "$eq": ["$ammonia", 10]}, "then": "sedikit"},
                                    {"case": {
                                        "$eq": ["$ammonia", 25]}, "then": "aman"},
                                    {"case": {
                                        "$eq": ["$ammonia", 50]}, "then": "pekat"},
                                    {"case": {
                                        "$eq": ["$ammonia", 100]}, "then": "banyak"},
                                    {"case": {
                                        "$eq": ["$ammonia", 250]}, "then": "berbahaya"},
                                    {"case": {
                                        "$eq": ["$ammonia", 500]}, "then": "deadzone"},
                                ],
                                "default": "normal"
                            }
                    },
                    "ammonia_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {"case": {
                                        "$eq": ["$ammonia", 0]}, "then": "sedikit"},
                                    {"case": {
                                        "$eq": ["$ammonia", 0.25]}, "then": "aman"},
                                    {"case": {
                                        "$eq": ["$ammonia", 1.5]}, "then": "pekat"},
                                    {"case": {
                                        "$eq": ["$ammonia", 3]}, "then": "banyak"},
                                    {"case": {
                                        "$eq": ["$ammonia", 5]}, "then": "berbahaya"},
                                ],
                                "default": "normal"
                            }
                    },
                    "hardness_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {"case": {
                                        "$eq": ["$ammonia", 0]}, "then": "sedikit"},
                                    {"case": {
                                        "$eq": ["$ammonia", 25]}, "then": "aman"},
                                    {"case": {
                                        "$eq": ["$ammonia", 50]}, "then": "pekat"},
                                    {"case": {
                                        "$eq": ["$ammonia", 125]}, "then": "banyak"},
                                    {"case": {
                                        "$eq": ["$ammonia", 250]}, "then": "berbahaya"},
                                    {"case": {
                                        "$eq": ["$ammonia", 425]}, "then": "deadzone"},
                                ],
                                "default": "normal"
                            }
                    },
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            weeklywaterquality = WeeklyWaterQuality.objects.aggregate(pipeline)
            list_weeklywaterqualitys = list(weeklywaterquality)
            response = json.dumps(list_weeklywaterqualitys, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def post(self):
        try:
            pond_id = request.form.get("pond_id", None)
            pond = Pond.objects.get(id=pond_id)
            if pond['isActive'] == False:
                response = {"message": "pond is not active"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            pond_activation = PondActivation.objects(
                pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
            body = {
                "pond_id": pond.id,
                "pond_activation_id": pond_activation.id,
                "floc": request.form.get("floc", None),
                "nitrite": request.form.get("nitrite", None),
                "nitrate": request.form.get("nitrate", None),
                "ammonia": request.form.get("ammonia", None),
                "hardness": request.form.get("hardness", None),
            }
            weeklywaterquality = WeeklyWaterQuality(**body).save()
            id = weeklywaterquality.id
            response = {
                "message": "success add data weekly water quality", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class WeeklyWaterQualityApi(Resource):
    def put(self, id):
        try:
            body = request.form.to_dict(flat=True)
            WeeklyWaterQuality.objects.get(id=id).update(**body)
            response = {
                "message": "success change data weekly water quality", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def delete(self, id):
        try:
            weeklywaterquality = WeeklyWaterQuality.objects.get(id=id).delete()
            response = {"message": "success delete weekly water quality"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def get(self, id):
        try:
            pipeline = [
                {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': id}]}}},
                {"$sort": {"created_at": -1}},
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                        {"$project": {
                            "_id": 1,
                            "alias": 1,
                            "location": 1,
                            "build_at": 1,
                            "isActive": 1,
                        }}
                    ],
                    'as': 'pond'
                }},
                {'$lookup': {
                    'from': 'pond_activation',
                    'let': {"activationid": "$pond_activation_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$activationid']}}},
                        {"$project": {
                            "_id": 1,
                            "isFinish": 1,
                            "isWaterPreparation": 1,
                            "water_level": 1,
                            "activated_at": 1
                        }}
                    ],
                    'as': 'pond_activation'
                }},
                {"$addFields": {
                    "pond": {"$first": "$pond"},
                    "pond_activation": {"$first": "$pond_activation"},
                    "floc_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {"case": {
                                        "$eq": ["$floc", "0-10"]}, "then": "pembentukan"},
                                    {"case": {
                                        "$eq": ["$floc", "11-30"]}, "then": "normal"},
                                    {"case": {
                                        "$eq": ["$floc", "31-50"]}, "then": "tebal"},
                                    {"case": {
                                        "$eq": ["$floc", "51-100"]}, "then": "abnormal"},
                                    {"case": {
                                        "$eq": ["$floc", "101-300"]}, "then": "berbahaya"},
                                    {"case": {
                                        "$eq": ["$floc", ">300"]}, "then": "deadzone"},
                                ],
                                "default": "normal"
                            }
                    },
                    "nitrite_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {"case": {
                                        "$eq": ["$ammonia", 0]}, "then": "tidak ada"},
                                    {"case": {
                                        "$eq": ["$ammonia", 1]}, "then": "sedikit"},
                                    {"case": {
                                        "$eq": ["$ammonia", 5]}, "then": "aman"},
                                    {"case": {
                                        "$eq": ["$ammonia", 10]}, "then": "pekat"},
                                    {"case": {
                                        "$eq": ["$ammonia", 20]}, "then": "banyak"},
                                    {"case": {
                                        "$eq": ["$ammonia", 40]}, "then": "berbahaya"},
                                    {"case": {
                                        "$eq": ["$ammonia", 80]}, "then": "deadzone"},
                                ],
                                "default": "normal"
                            }
                    },
                    "nitrate_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {"case": {
                                        "$eq": ["$ammonia", 0]}, "then": "tidak ada"},
                                    {"case": {
                                        "$eq": ["$ammonia", 10]}, "then": "sedikit"},
                                    {"case": {
                                        "$eq": ["$ammonia", 25]}, "then": "aman"},
                                    {"case": {
                                        "$eq": ["$ammonia", 50]}, "then": "pekat"},
                                    {"case": {
                                        "$eq": ["$ammonia", 100]}, "then": "banyak"},
                                    {"case": {
                                        "$eq": ["$ammonia", 250]}, "then": "berbahaya"},
                                    {"case": {
                                        "$eq": ["$ammonia", 500]}, "then": "deadzone"},
                                ],
                                "default": "normal"
                            }
                    },
                    "ammonia_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {"case": {
                                        "$eq": ["$ammonia", 0]}, "then": "sedikit"},
                                    {"case": {
                                        "$eq": ["$ammonia", 0.25]}, "then": "aman"},
                                    {"case": {
                                        "$eq": ["$ammonia", 1.5]}, "then": "pekat"},
                                    {"case": {
                                        "$eq": ["$ammonia", 3]}, "then": "banyak"},
                                    {"case": {
                                        "$eq": ["$ammonia", 5]}, "then": "berbahaya"},
                                ],
                                "default": "normal"
                            }
                    },
                    "hardness_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {"case": {
                                        "$eq": ["$ammonia", 0]}, "then": "sedikit"},
                                    {"case": {
                                        "$eq": ["$ammonia", 25]}, "then": "aman"},
                                    {"case": {
                                        "$eq": ["$ammonia", 50]}, "then": "pekat"},
                                    {"case": {
                                        "$eq": ["$ammonia", 125]}, "then": "banyak"},
                                    {"case": {
                                        "$eq": ["$ammonia", 250]}, "then": "berbahaya"},
                                    {"case": {
                                        "$eq": ["$ammonia", 425]}, "then": "deadzone"},
                                ],
                                "default": "normal"
                            }
                    },
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            weeklywaterquality = WeeklyWaterQuality.objects.aggregate(pipeline)
            list_weeklywaterqualitys = list(weeklywaterquality)
            response = json.dumps(list_weeklywaterqualitys[0], default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

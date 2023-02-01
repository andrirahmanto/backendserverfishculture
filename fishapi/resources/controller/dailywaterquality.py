from flask import Response, request
from fishapi.database.models import DailyWaterQuality, Pond, PondActivation
from flask_restful import Resource
import datetime
import json


class DailyWaterQualitysApi(Resource):
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
                    "ph_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {
                                        "case": {"$lt": ["$ph", 6]},
                                        "then": "berbahaya"
                                    },
                                    {
                                        "case": {"$gt": ["$ph", 8]},
                                        "then": "berbahaya"
                                    }
                                ],
                                "default": "normal"
                            }
                    },
                    "do_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {
                                        "case": {"$or": [
                                            {"$lt": ["$do", 3]},
                                            {"$gt": ["$do", 7.5]}
                                        ]},
                                        "then": "berbahaya"
                                    },
                                    {
                                        "case": {"$or": [
                                            {"$and": [{"$gte": ["$do", 3]}, {
                                                "$lte": ["$do", 4]}]},
                                            {"$and": [{"$gt": ["$do", 6]}, {
                                                "$lte": ["$do", 7.5]}]}
                                        ]},
                                        "then": "semi berbahaya"
                                    }
                                ],
                                "default": "normal"
                            }
                    }
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            dailywaterquality = DailyWaterQuality.objects.aggregate(pipeline)
            list_dailywaterqualitys = list(dailywaterquality)
            response = json.dumps(list_dailywaterqualitys, default=str)
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
                "ph": request.form.get("ph", None),
                "do": request.form.get("do", None),
                "temperature": request.form.get("temperature", None),
            }
            print(body)
            if int(request.form.get("ph")) < 6 or int(request.form.get("ph")) > 8:
                pond.update(**{"pondPhDesc": "berbahaya", "pondPh": int(request.form.get("ph"))})
            else:
                pond.update(**{"pondPhDesc": "normal", "pondPh": int(request.form.get("ph"))})
            if float(request.form.get("do")) < 3 or float(request.form.get("do")) > 7.5:
                pond.update(**{"pondDoDesc": "berbahaya", "pondDo": float(request.form.get("do"))})
            elif float(request.form.get("do")) >= 3 and float(request.form.get("do")) <= 4 or float(request.form.get("do")) >= 6 and float(request.form.get("Do")) <= 7.5:
                pond.update(**{"pondDoDesc": "semi berbahaya", "pondDo": float(request.form.get("do"))})
            else:
                pond.update(**{"pondDoDesc": "normal", "pondDo": float(request.form.get("do"))})
            pond.update(**{"pondTemp": int(request.form.get("temperature"))})
            dailywaterquality = DailyWaterQuality(**body).save()
            id = dailywaterquality.id
            response = {
                "message": "success add data daily water quality", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class DailyWaterQualityApi(Resource):
    def put(self, id):
        try:
            body = request.form.to_dict(flat=True)
            DailyWaterQuality.objects.get(id=id).update(**body)
            response = {
                "message": "success change data daily water quality", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def delete(self, id):
        try:
            dailywaterquality = DailyWaterQuality.objects.get(id=id).delete()
            response = {"message": "success delete daily water quality"}
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
                    "ph_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {
                                        "case": {"$lt": ["$ph", 6]},
                                        "then": "berbahaya"
                                    },
                                    {
                                        "case": {"$gt": ["$ph", 8]},
                                        "then": "berbahaya"
                                    }
                                ],
                                "default": "normal"
                            }
                    },
                    "do_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {
                                        "case": {"$or": [
                                            {"$lt": ["$do", 3]},
                                            {"$gt": ["$do", 7.5]}
                                        ]},
                                        "then": "berbahaya"
                                    },
                                    {
                                        "case": {"$or": [
                                            {"$and": [{"$gte": ["$do", 3]}, {
                                                "$lte": ["$do", 4]}]},
                                            {"$and": [{"$gt": ["$do", 6]}, {
                                                "$lte": ["$do", 7.5]}]}
                                        ]},
                                        "then": "semi berbahaya"
                                    }
                                ],
                                "default": "normal"
                            }
                    }
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            dailywaterquality = DailyWaterQuality.objects.aggregate(pipeline)
            list_dailywaterqualitys = list(dailywaterquality)
            response = json.dumps(list_dailywaterqualitys[0], default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

from flask import Response, request
from fishapi.database.models import FishGrading, Pond, PondActivation
from flask_restful import Resource
import datetime
import json


class FishGradingsApi(Resource):
    def get(self):
        try:
            pipeline = [
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
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            fishgrading = FishGrading.objects.aggregate(pipeline)
            list_fishgradings = list(fishgrading)
            response = json.dumps(list_fishgradings, default=str)
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
                "fish_type": request.form.get("fish_type", None),
                "sampling_amount": request.form.get("sampling_amount", None),
                "avg_fish_weight": request.form.get("avg_fish_weight", None),
                "avg_fish_long": request.form.get("avg_fish_long", None),
                "amount_normal_fish": request.form.get("amount_normal_fish", None),
                "amount_oversize_fish": request.form.get("amount_oversize_fish", None),
                "amount_undersize_fish": request.form.get("amount_undersize_fish", None),
                "created_at": created_at,
                "grading_at": created_at,
            }
            fishgrading = FishGrading(**body).save()
            id = fishgrading.id
            return {'id': str(id)}, 200
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FishGradingApi(Resource):
    def put(self, id):
        try:
            body = request.form.to_dict(flat=True)
            FishGrading.objects.get(id=id).update(**body)
            response = {
                "message": "success change data fish grading", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def delete(self, id):
        try:
            fishgrading = FishGrading.objects.get(id=id).delete()
            response = {"message": "success delete fish grading"}
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
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            fishgrading = FishGrading.objects.aggregate(pipeline)
            list_fishgradings = list(fishgrading)
            response = json.dumps(list_fishgradings[0], default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FishGradingGraphApi(Resource):
    def get(self):
        # setup months
        year = datetime.datetime.today().year
        months = ["01", "02", "03", "04", "05",
                  "06", "07", "08", "09", "10", "11", "12"]
        for i in range(len(months)):
            months[i] = str(year) + "-" + months[i]

        # set empty list
        nilamerah = []
        nilahitam = []
        lele = []
        mas = []
        patin = []

        # get weight fish in this month
        # nila hitam
        for i in range(len(months)):
            grading_nilahitam = FishGrading.objects.aggregate([
                {'$match': {'$expr': {'$and': [
                    {'$eq': [months[i], {'$dateToString': {
                            'format': '%Y-%m', 'date': "$created_at"}}]},
                    {'$eq': ['$fish_type', 'nila hitam']}
                ]
                }}},
            ])
            grading_nilahitam = list(grading_nilahitam)
            if len(grading_nilahitam) < 1:
                nilahitam.append(0)
                continue
            weight_nilahitam = 0
            for grd_nilahitam in grading_nilahitam:
                weight_nilahitam += grd_nilahitam["avg_fish_weight"]
            nilahitam.append(weight_nilahitam/len(grading_nilahitam))

        # nila merah
        for i in range(len(months)):
            grading_nilamerah = FishGrading.objects.aggregate([
                {'$match': {'$expr': {'$and': [
                    {'$eq': [months[i], {'$dateToString': {
                            'format': '%Y-%m', 'date': "$created_at"}}]},
                    {'$eq': ['$fish_type', 'nila merah']}
                ]
                }}},
            ])
            grading_nilamerah = list(grading_nilamerah)
            if len(grading_nilamerah) < 1:
                nilamerah.append(0)
                continue
            weight_nilamerah = 0
            for grd_nilamerah in grading_nilamerah:
                weight_nilamerah += grd_nilamerah["avg_fish_weight"]
            nilamerah.append(weight_nilamerah/len(grading_nilamerah))

        # lele
        for i in range(len(months)):
            grading_lele = FishGrading.objects.aggregate([
                {'$match': {'$expr': {'$and': [
                    {'$eq': [months[i], {'$dateToString': {
                            'format': '%Y-%m', 'date': "$created_at"}}]},
                    {'$eq': ['$fish_type', 'lele']}
                ]
                }}},
            ])
            grading_lele = list(grading_lele)
            if len(grading_lele) < 1:
                lele.append(0)
                continue
            weight_lele = 0
            for grd_lele in grading_lele:
                weight_lele += grd_lele["avg_fish_weight"]
            lele.append(weight_lele/len(grading_lele))

        # mas
        for i in range(len(months)):
            grading_mas = FishGrading.objects.aggregate([
                {'$match': {'$expr': {'$and': [
                    {'$eq': [months[i], {'$dateToString': {
                            'format': '%Y-%m', 'date': "$created_at"}}]},
                    {'$eq': ['$fish_type', 'mas']}
                ]
                }}},
            ])
            grading_mas = list(grading_mas)
            if len(grading_mas) < 1:
                mas.append(0)
                continue
            weight_mas = 0
            for grd_mas in grading_mas:
                weight_mas += grd_mas["avg_fish_weight"]
            mas.append(weight_mas/len(grading_mas))

        # patin
        for i in range(len(months)):
            grading_patin = FishGrading.objects.aggregate([
                {'$match': {'$expr': {'$and': [
                    {'$eq': [months[i], {'$dateToString': {
                            'format': '%Y-%m', 'date': "$created_at"}}]},
                    {'$eq': ['$fish_type', 'patin']}
                ]
                }}},
            ])
            grading_patin = list(grading_patin)
            if len(grading_patin) < 1:
                patin.append(0)
                continue
            weight_patin = 0
            for grd_patin in grading_patin:
                weight_patin += grd_patin["avg_fish_weight"]
            patin.append(weight_patin/len(grading_patin))

        response = {
            "nila merah": nilamerah,
            "nila hitam": nilahitam,
            "lele": lele,
            "mas": mas,
            "patin": patin,
        }
        response = {
            "nila merah": [0.4, 1.1, 2, 2.1, 3.2, 3.4, 4, 4.3],
            "nila hitam": [0.4, 0.6, 3, 3.1, 3.8, 4, 4.3, 4.6],
            "lele": [1, 1.5, 2.1, 2.3, 2.6, 3.1, 4, 4.2],
            "mas": [0.1, 0.4, 0.8, 1.2, 3, 4, 5, 5.5],
            "patin": [0, 0, 0, 0, 0, 0, 0, 0],
        }
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)


class FishGradingApiByActivation(Resource):
    def get(self, activation_id):
        try:
            pipeline = [
                {'$match': {
                    '$expr': {'$eq': ['$pond_activation_id', {'$toObjectId': activation_id}]}}},
                {'$lookup': {
                    'from': 'pond_activation',
                    'let': {"activationid": "$pond_activation_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$activationid']}}},
                    ],
                    'as': 'pond_activation'
                }},
                {"$addFields": {
                    "constanta_oversize": {"$first": "$pond_activation.constanta_oversize"},
                    "constanta_undersize": {"$first": "$pond_activation.constanta_undersize"},
                }},
                {"$project": {
                    "pond_activation": 0,
                    "updated_at": 0,
                    "created_at": 0,
                }},
                {"$sort": {"grading_at": -1}}
            ]
            fishgrading = FishGrading.objects.aggregate(pipeline)
            list_fishgradings = list(fishgrading)
            response = json.dumps(list_fishgradings, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

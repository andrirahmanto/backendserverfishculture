from flask import Response, request
from fishapi.database.models import *
from flask_restful import Resource
import datetime
import json


class PondTreatmentsApi(Resource):
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
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            pondtreatment = PondTreatment.objects.aggregate(pipeline)
            list_pondtreatments = list(pondtreatment)
            response = json.dumps(list_pondtreatments, default=str)
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
            treatment_type = request.form.get("treatment_type", None)
            if treatment_type == "berat":
                fishes = request.form.get("fish", "[]")
                fishes = json.loads(fishes)
                body = {
                    "pond_id": pond_id,
                    "pond_activation_id": pond_activation.id,
                    "treatment_type": treatment_type,
                    "water_change": 100,
                    "description": request.form.get("description", None),
                }
                pondtreatment = PondTreatment(**body).save()
                id = pondtreatment.id
                # update activation and pond
                pond_deactivation_data = {
                    "isFinish": True,
                    "total_fish_harvested": request.form.get("total_fish_harvested", None),
                    "total_weight_harvested": request.form.get("total_weight_harvested", None),
                    "deactivated_at": request.form.get("deactivated_at", datetime.datetime.now()),
                    "deactivated_description": "karantina total"
                }
                pond_activation = PondActivation.objects(
                    pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
                pond_activation.update(**pond_deactivation_data)
                pond.update(**{"isActive": False, "status": "Panen"})
                for fish in fishes:
            # save fish log
                    data = {
                        "pond_id": pond_id,
                        "pond_activation_id": pond_activation.id,
                        "type_log": "deactivation",
                        "fish_type": fish['type'],
                        "fish_amount": fish['amount'],
                        "fish_total_weight": fish['weight']
                    }
                    # total_fish_harvested += fish['amount']
                    # total_weight_harvested += fish['weight']
                    fishlog = FishLog(**data).save()
                    print(data)
            elif treatment_type == "ringan":
                body = {
                    "pond_id": pond_id,
                    "pond_activation_id": pond_activation.id,
                    "treatment_type": treatment_type,
                    "description": request.form.get("description", None),
                    "water_change": request.form.get("water_change", 0),
                    "salt": request.form.get("salt", None),
                    "probiotic_culture": request.form.get("probiotic_culture", None),
                    "carbohydrate": request.form.get("carbohydrate", None),
                    "carbohydrate_type": request.form.get("carbohydrate_type", None),
                    "treatment_at": request.form.get("treatment_at", datetime.datetime.now())
                }
                pondtreatment = PondTreatment(**body).save()
                id = pondtreatment.id
            elif treatment_type == "pergantian air":
                body = {
                    "pond_id": pond_id,
                    "pond_activation_id": pond_activation.id,
                    "treatment_type": treatment_type,
                    "water_change": request.form.get("water_change", 0)
                }
                pondtreatment = PondTreatment(**body).save()
                id = pondtreatment.id
            else:
                response = {
                    "message": "treatment type just allow ['ringan','berat']"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            response = {
                "message": "success add data pond treatment", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class PondTreatmentApi(Resource):
    def put(self, id):
        try:
            body = request.form.to_dict(flat=True)
            PondTreatment.objects.get(id=id).update(**body)
            response = {
                "message": "success change data pond treatment", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def delete(self, id):
        try:
            pondtreatment = PondTreatment.objects.get(id=id).delete()
            response = {"message": "success delete pond treatment"}
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
            pondtreatment = PondTreatment.objects.aggregate(pipeline)
            list_pondtreatments = list(pondtreatment)
            response = json.dumps(list_pondtreatments[0], default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

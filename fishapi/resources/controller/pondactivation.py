from flask import Response, request
from fishapi.database.models import *
from flask_restful import Resource
from fishapi.database.db import db
import datetime
import json
from bson.json_util import dumps


class PondsStatusApi(Resource):
    def get(self):
        pass


class PondStatusApi(Resource):
    def get(self, pond_id):
        pass


class PondActivationApi(Resource):
    def post(self, pond_id):
        pond = Pond.objects.get(id=pond_id)
        if pond.isActive == True:
            response = {"message": "status pond is already active"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        fish = request.form.get("fish", "[]")
        fish = json.loads(fish)
        water_preparation = request.form.get("water_preparation", False)
        if water_preparation == "true":
            water_preparation = True
        else:
            False
        water_level = request.form.get("water_level", None)
        activated_at = request.form.get(
            "activated_at", datetime.datetime.now())
        activation_data = {
            "fish": fish,
            "water_preparation": water_preparation,
            "water_level": water_level,
            "activated_at": activated_at
        }
        activation = Activation(**activation_data).save()
        activation_id = activation.id
        if water_preparation == True:
            carbohydrate = request.form.get("carbohydrate", None)
            carbohydrate_type = request.form.get("carbohydrate_type", None)
            salt = request.form.get("salt", None)
            calcium = request.form.get("calcium", None)
            water_preparation_data = {
                "activation_id": activation_id,
                "carbohydrate": carbohydrate,
                "carbohydrate_type": carbohydrate_type,
                "salt": salt,
                "calcium": calcium,
            }
            water_preparation = WaterPreparation(
                **water_preparation_data).save()
        pond_status_data = {
            "pond_id": pond_id,
            "activation_id": activation_id
        }
        pond_status = PondStatus(**pond_status_data).save()
        print(pond_status.id)
        pond.update(**{"isActive": True})
        response = {"message": "success to activation pond"}
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)


class PondDiactivationApi(Resource):
    def post(self, pond_id):
        pass

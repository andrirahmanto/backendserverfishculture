import os
from flask import Flask, Response, request, current_app, url_for, send_from_directory
from fishapiv2.database.models import *
from flask_restful import Resource
from werkzeug.utils import secure_filename
from fishapiv2.resources.helper import *
from fishapiv2.resources.controller.authentication import *
import datetime
import json
from mongoengine import ObjectIdField
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from bson.objectid import ObjectId

class BreederApi(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            id = str(current_user['id'])
            farm_id = str(current_user['farm_id'])
            farm_id = ObjectId(farm_id)
            id = ObjectId(id)
            pipeline_user = [
                {"$match": {"_id": id}},
            ]
            pipeline_farm = [
                {"$match": {"_id": farm_id}},
            ]
            breeder = Breeder.objects.aggregate(pipeline_user)
            farmdata = Farm.objects.aggregate(pipeline_farm)
            list_farm = list(farmdata)
            list_breeder = list(breeder)
            breederdata = {
                "username": list_breeder[0]['username'],
                "name": list_breeder[0]['name'],
                "nik": list_breeder[0]['nik'],
                "phone": list_breeder[0]['phone'],
                "farm_name": list_farm[0]['farm_name'],
                "address": list_farm[0]['address'],
                "farm_id": list_breeder[0]["farm_id"]
            }
            response = json.dumps(breederdata, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
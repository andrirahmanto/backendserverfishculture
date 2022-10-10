import os
from flask import Flask, Response, request, current_app, url_for, send_from_directory
from fishapi.database.models import *
from flask_restful import Resource
from werkzeug.utils import secure_filename
from fishapi.resources.helper import *
import datetime
import json


class FishDeathsApi(Resource):
    def get(self):
        try:
            url = url_for('fishdeathimageapidummy', _external=True)
            pipeline = [
                {'$lookup': {
                    'from': 'pond_activation',
                    'let': {"pondid": "$_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_id', '$$pondid']},
                            {'$eq': ['$isFinish', False]},
                        ]}}},
                        {"$lookup": {
                            "from": "fish_death",
                            "let": {"activationid": "$_id"},
                            "pipeline": [
                                {'$match': {'$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$activationid']},
                                ]}}},
                                {'$lookup': {
                                    'from': 'fish_log',
                                    'let': {"fish_death_id": "$_id"},
                                    'pipeline': [
                                        {'$match': {
                                            '$expr': {'$and': [
                                                {'$eq': ['$fish_death_id',
                                                         '$$fish_death_id']},
                                                {'$eq': ['$type_log',
                                                         'death']},
                                            ]}
                                        }},
                                        {"$project": {
                                            "created_at": 0,
                                            "updated_at": 0,
                                        }}
                                    ],
                                    'as': 'fish'
                                }},
                                {"$addFields": {
                                    "image_link": {"$concat": [url, "/", {"$toString": "$_id"}]}
                                }},
                                {"$project": {
                                    "pond_id": 0,
                                    "pond_activation_id": 0,
                                    "created_at": 0,
                                    "updated_at": 0,
                                }}
                            ],
                            "as": "fish_death_list",
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
                    "pond_activation": {"$first": "$pond_activation_list"},
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
            ponds = Pond.objects.aggregate(pipeline)
            list_ponds = list(ponds)
            response = json.dumps(list_ponds, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def post(self):
        try:
            pond_id = request.form.get("pond_id", None)
            pond = Pond.objects.get(id=pond_id)
            if pond.isActive == False:
                response = {"message": "status pond is not active"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            pond_activation = PondActivation.objects(
                pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
            try:
                file = request.files['image', None]
                if not allowed_file(file.filename):
                    response = {"message": "file type not allowed"}
                    response = json.dumps(response, default=str)
                    return Response(response, mimetype="application/json", status=400)
                filename = secure_filename(file.filename)
                filename = pad_timestamp(filename)
                path = os.path.join(current_app.instance_path,
                                    current_app.config['UPLOAD_DIR'])
                try:
                    os.makedirs(path)
                except OSError:
                    pass
                filepath = os.path.join(path, filename)
                file.save(filepath)
            except:
                filename = "default.jpg"
            fish_death_amount = request.form.get("fish_death_amount", "[]")
            fish_death_amount = json.loads(fish_death_amount)
            if len(fish_death_amount) < 1:
                response = {"message": "There is no fish"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            body = {
                "pond_id": pond.id,
                "pond_activation_id": pond_activation.id,
                "image_name": filename,
                "diagnosis": request.form.get("diagnosis", None),
            }
            fishdeath = FishDeath(**body).save()
            id = fishdeath.id
            for fish in fish_death_amount:
                # save fish log
                data = {
                    "pond_id": pond_id,
                    "pond_activation_id": pond_activation.id,
                    "fish_death_id": id,
                    "type_log": "death",
                    "fish_type": fish['type'],
                    "fish_amount": int(fish['amount']) * -1
                }
                fishlog = FishLog(**data).save()
            response = {"message": "success add fishdeath"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FishDeathApi(Resource):
    def put(self, id):
        try:
            body = request.form.to_dict(flat=True)
            FishDeath.objects.get(id=id).update(**body)
            response = {"message": "success change data fish death", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        return

    def delete(self, id):
        try:
            fishdeath = FishDeath.objects.get(id=id)
            # delete picture
            path = os.path.join(current_app.instance_path,
                                current_app.config['UPLOAD_DIR'])
            os.remove(os.path.join(path, fishdeath['image_name']))
            # delete data
            fishdeath.delete()
            response = {"message": "success delete pond"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FishDeathImageApiDummy(Resource):
    def get(self):
        pass


class FishDeathImageApi(Resource):
    def get(self, id):
        objects = FishDeath.objects.get(id=id)
        fishdeath = objects.to_mongo()
        path = os.path.join(current_app.instance_path,
                            current_app.config['UPLOAD_DIR'])
        return send_from_directory(path, fishdeath['image_name'])


class FishDeathsApiByActivation(Resource):
    def get(self, activation_id):
        try:
            print(activation_id)
            url = url_for('fishdeathimageapidummy', _external=True)
            pipeline = [
                {'$match': {'$expr': {'$and': [
                    {'$eq': ['$pond_activation_id',
                             {"$toObjectId": activation_id}]},
                ]}}},
                {'$lookup': {
                    'from': 'fish_log',
                    'let': {"fish_death_id": "$_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$and': [
                                {'$eq': ['$fish_death_id',
                                         '$$fish_death_id']},
                                {'$eq': ['$type_log',
                                         'death']},
                            ]}
                        }},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'fish'
                }},
                {"$unwind": "$fish"},
                {"$sort": {"death_at": -1}}
            ]
            fishdeaths = FishDeath.objects.aggregate(pipeline)
            fishdeaths = list(fishdeaths)
            response = json.dumps(fishdeaths, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

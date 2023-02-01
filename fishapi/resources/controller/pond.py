import os
from flask import Flask, Response, request, current_app, url_for, send_from_directory
from fishapi.database.models import *
from flask_restful import Resource
from werkzeug.utils import secure_filename
from fishapi.resources.helper import *
import datetime
import json


class PondsApi(Resource):
    def get(self):
        try:
            url = url_for('pondimageapidummy', _external=True)
            pipeline = [
                {"$sort": {"status": 1,"alias": 1}},
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
                            'as': 'fish_alive'
                        }},
                        {"$addFields": {
                            "activated_at": {'$dateToString': {
                                'format': "%d-%m-%Y", 'date': "$activated_at"}},
                            "deactivated_at": {'$dateToString': {
                                'format': "%d-%m-%Y", 'date': "$deactivated_at"}},
                            "total_fish_alive": {"$sum": "$fish_alive.fish_amount"}
                        }},
                        {"$project": {
                            "pond_id": 0,
                            "feed_type_id": 0,
                            "created_at": 0,
                            "updated_at": 0,
                        }},
                    ],
                    'as': 'pond_activation_list'
                }},
                {"$addFields": {
                    "area": {"$cond": {
                        "if": {"$eq": ["$shape", "persegi"]},
                        "then": {"$multiply": ["$length", "$width"]},
                        "else": {"$divide": [
                            {"$multiply": [22, "$diameter", "$diameter"]},
                            28
                        ]},
                    }},
                    "image_link":{"$concat": [url, "/", {"$toString": "$_id"}]}
                }},
                {"$addFields": {
                    "volume": {"$multiply": ["$area", "$height"]},
                    "last_activation": {"$first": "$pond_activation_list"},
                    "status": {
                        "$switch":
                        {
                            "branches": [
                                {
                                    "case": {"$eq": ["$isActive", True]},
                                    "then": "Aktif"
                                },
                                {
                                    "case": {"$and": [
                                        {"$eq": ["$isActive", False]},
                                        {"$lt": [
                                            {"$size": "$pond_activation_list"}, 1]}
                                    ]},
                                    "then": "Tidak Aktif"
                                }
                            ],
                            "default": "Panen"
                        }
                    },
                }},
                {"$addFields": {
                    "activation_date": "$last_activation.activated_at",
                    "fish_alive": "$last_activation.total_fish_alive",
                }},
                {"$project": {
                    "pond_id": 0,
                    "feed_type_id": 0,
                    "created_at": 0,
                    "updated_at": 0,
                    "pond_activation_list": 0,
                    "last_activation": 0,
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
            body = {
                "alias": request.form.get("alias", None),
                "location": request.form.get("location", None),
                "shape": request.form.get("shape", None),
                "material": request.form.get("material", None),
                "length": request.form.get("length", None),
                "width": request.form.get("width", None),
                "status": request.form.get("status",None),
                "diameter": request.form.get("diameter", None),
                "height": request.form.get("height", None),
                "build_at": request.form.get("build_at", None),
            }
            pond = Pond(**body).save()
            id = pond.id
            response = {"message": "success add pond", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class PondApi(Resource):
    def put(self, id):
        try:
            body = request.form.to_dict(flat=True)
            Pond.objects.get(id=id).update(**body)
            response = {"message": "success change data pond", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        return

    def delete(self, id):
        try:
            pond = Pond.objects.get(id=id).delete()
            response = {"message": "success delete pond"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def get(self, id):
        try:
            objects = Pond.objects.get(id=id)
            pond = objects.to_mongo()
            response_dump = json.dumps(pond, default=str)
            return Response(response_dump, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class PondImageApiDummy(Resource):
    def get(self):
        pass


class PondImageApi(Resource):
    def get(self, id):
        # init object pond
        objects = Pond.objects.get(id=id)
        # convert to dict
        pond = objects.to_mongo()
        # dump dict to json string
        path = os.path.join(current_app.instance_path,
                            current_app.config['UPLOAD_DIR'])
        return send_from_directory(path, pond['image_name'])

    def put(self, id):
        try:
            file = request.files['image']
            if not file:
                response = {"message": "no file selected"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
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
            # database
            objects = Pond.objects.get(id=id)
            pond = objects.to_mongo()
            old_image_name = pond["image_name"]
            new_image_name = filename
            if old_image_name != "default.jpg":
                os.remove(os.path.join(path, old_image_name))
            data = {
                "image_name": new_image_name
            }
            objects.update(**data)
            id = objects.id
            response = {"message": "success change image", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

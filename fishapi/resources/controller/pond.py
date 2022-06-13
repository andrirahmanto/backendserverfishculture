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
        url = url_for('pondimageapidummy', _external=True)
        pipeline = [
            {'$lookup': {
                'from': 'pond_image',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$eq': ['$pond_id', '$$pondid']}}},
                    {"$addFields": {
                        "link": {"$concat": [url, "/", {"$toString": "$pond_id"}]}
                    }},
                ],
                'as': 'pond_image'
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
                "pond_image":{"$first": "$pond_image"}
            }},
            {"$addFields": {
                "volume": {"$multiply": ["$area", "$height"]}
            }},
            {"$project": {
                "pond_id": 0,
                "feed_type_id": 0,
                "created_at": 0,
                "updated_at": 0,
            }}
        ]
        ponds = Pond.objects.aggregate(pipeline)
        list_ponds = list(ponds)
        response = json.dumps(list_ponds, default=str)
        return Response(response, mimetype="application/json", status=200)

    def post(self):
        body = {
            "alias": request.form.get("alias", None),
            "location": request.form.get("location", None),
            "shape": request.form.get("shape", None),
            "material": request.form.get("material", None),
            "length": request.form.get("length", None),
            "width": request.form.get("width", None),
            "diameter": request.form.get("diameter", None),
            "height": request.form.get("height", None),
            "build_at": request.form.get("build_at", None),
        }
        pond = Pond(**body).save()
        id = pond.id
        return {'id': str(id)}, 200


class PondImageApiDummy(Resource):
    def get(self):
        pass


class PondImageApi(Resource):
    def get(self, id):
        # init object pond
        objects = PondImage.objects.get(pond_id=id)
        # convert to dict
        pond = objects.to_mongo()
        # dump dict to json string
        path = os.path.join(current_app.instance_path,
                            current_app.config['UPLOAD_DIR'])
        return send_from_directory(path, pond['image_name'])

    def post(self, id):
        file = request.files['image']

        if file and allowed_file(file.filename):
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

            # save to db
            data = {
                "pond_id": id,
                "image_name": filename
            }
            pondimage = PondImage(**data).save()
            id = pondimage.id
            return {'id': str(id)}, 200

        response = {"message": str(e)}
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=400)

    def put(self, id):
        pass


class PondApi(Resource):
    def put(self, id):
        body = {
            "alias": request.form.get("alias", None),
            "location": request.form.get("location", None),
            "updated_at": datetime.datetime.utcnow()
        }
        Pond.objects.get(id=id).update(**body)
        return '', 200

    def delete(self, id):
        pond = Pond.objects.get(id=id).delete()
        return '', 200

    def get(self, id):
        # init object pond
        objects = Pond.objects.get(id=id)
        # convert to dict
        pond = objects.to_mongo()
        # dump dict to json string
        response_dump = json.dumps(pond, default=str)
        return Response(response_dump, mimetype="application/json", status=200)

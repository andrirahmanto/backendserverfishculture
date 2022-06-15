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


class PondApi(Resource):
    def put(self, id):
        try:
            body = {
                "alias": request.form.get("alias", None),
                "location": request.form.get("location", None),
                "updated_at": datetime.datetime.utcnow()
            }
            Pond.objects.get(id=id).update(**body)
            response = {"message": "success change data pond", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

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

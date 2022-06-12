from flask import Response, request
from fishapi.database.models import Pond
from flask_restful import Resource
import datetime
import json


class PondsApi(Resource):
    def get(self):
        pipeline = [
            {"$addFields": {
                "area": {"$cond": {
                    "if": {"$eq": ["$shape", "persegi"]},
                    "then": {"$multiply": ["$length", "$width"]},
                    "else": {"$divide": [
                        {"$multiply": [22, "$diameter", "$diameter"]},
                        28
                    ]},
                }}
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

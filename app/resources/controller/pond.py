from flask import Response, request
from app.database.models import Pond
from flask_restful import Resource
import datetime
import json


class PondsApi(Resource):
    def get(self):
        # init object pond
        objects = Pond.objects()
        # empty list for response
        response = []
        # access one feedhistory in objects
        for pond in objects:
            # convert to dict
            pond = pond.to_mongo()
            # add to list
            response.append(pond)
        # dump json to json string
        response_dump = json.dumps(response, default=str)
        return Response(response_dump, mimetype="application/json", status=200)

    def post(self):
        body = request.get_json()
        pond = Pond(**body).save()
        id = pond.id
        return {'id': str(id)}, 200


class PondApi(Resource):
    def put(self, id):
        body = request.get_json()
        body['updated_at'] = datetime.datetime.utcnow()
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

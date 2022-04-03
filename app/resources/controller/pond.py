from flask import Response, request
from app.database.models import Pond
from flask_restful import Resource
import datetime


class PondsApi(Resource):
    def get(self):
        ponds = Pond.objects().to_json()
        return Response(ponds, mimetype="application/json", status=200)

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
        pond = Pond.objects.get(id=id).to_json()
        return Response(pond, mimetype="application/json", status=200)

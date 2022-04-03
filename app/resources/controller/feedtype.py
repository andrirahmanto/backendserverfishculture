from flask import Response, request
from app.database.models import FeedType
from flask_restful import Resource
import datetime


class FeedTypesApi(Resource):
    def get(self):
        feedtypes = FeedType.objects().to_json()
        return Response(feedtypes, mimetype="application/json", status=200)

    def post(self):
        body = request.get_json()
        feedtype = FeedType(**body).save()
        id = feedtype.id
        return {'id': str(id)}, 200


class FeedTypeApi(Resource):
    def put(self, id):
        body = request.get_json()
        body['updated_at'] = datetime.datetime.utcnow()
        FeedType.objects.get(id=id).update(**body)
        return '', 200

    def delete(self, id):
        feedtype = FeedType.objects.get(id=id).delete()
        return '', 200

    def get(self, id):
        feedtype = FeedType.objects.get(id=id).to_json()
        return Response(feedtype, mimetype="application/json", status=200)

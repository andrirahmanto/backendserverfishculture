from flask import Response, request
from app.database.models import TypeFeed
from flask_restful import Resource
import datetime


class TypeFeedsApi(Resource):
    def get(self):
        typefeeds = TypeFeed.objects().to_json()
        return Response(typefeeds, mimetype="application/json", status=200)

    def post(self):
        body = request.get_json()
        typefeed = TypeFeed(**body).save()
        id = typefeed.id
        return {'id': str(id)}, 200


class TypeFeedApi(Resource):
    def put(self, id):
        body = request.get_json()
        body['updated_at'] = datetime.datetime.utcnow()
        TypeFeed.objects.get(id=id).update(**body)
        return '', 200

    def delete(self, id):
        typefeed = TypeFeed.objects.get(id=id).delete()
        return '', 200

    def get(self, id):
        typefeed = TypeFeed.objects.get(id=id).to_json()
        return Response(typefeed, mimetype="application/json", status=200)

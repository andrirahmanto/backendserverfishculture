from flask import Response, request
from fishapi.database.models import FeedType
from flask_restful import Resource
import datetime
import json


class FeedTypesApi(Resource):
    def get(self):
        # init object feedtype
        objects = FeedType.objects()
        # empty list for response
        response = []
        # access one feedhistory in objects
        for feedtype in objects:
            # convert to dict
            feedtype = feedtype.to_mongo()
            # add to list
            response.append(feedtype)
        # dump json to json string
        response_dump = json.dumps(response, default=str)
        return Response(response_dump, mimetype="application/json", status=200)

    def post(self):
        body = {
            "name": request.form.get("name", None),
            "feed_type": request.form.get("feed_type", None),
            "protein": request.form.get("protein", None),
            "carbohydrate": request.form.get("carbohydrate", None),
            "desc": request.form.get("desc", None)
        }
        feedtype = FeedType(**body).save()
        id = feedtype.id
        return {'id': str(id)}, 200


class FeedTypeApi(Resource):
    def put(self, id):
        body = {
            "name": request.form.get("name", None),
            "feed_type": request.form.get("feed_type", None),
            "protein": request.form.get("protein", None),
            "carbohydrate": request.form.get("carbohydrate", None),
            "desc": request.form.get("desc", None),
            "updated_at": datetime.datetime.utcnow()
        }
        FeedType.objects.get(id=id).update(**body)
        return '', 200

    def delete(self, id):
        feedtype = FeedType.objects.get(id=id).delete()
        return '', 200

    def get(self, id):
        # init object feedtype
        objects = FeedType.objects.get(id=id)
        # convert to dict
        feedtype = objects.to_mongo()
        # dump dict to json string
        response_dump = json.dumps(feedtype, default=str)
        return Response(response_dump, mimetype="application/json", status=200)

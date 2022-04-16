from flask import Response, request
from app.database.models import FeedHistory, Pond, FeedType
from flask_restful import Resource
import datetime
import json
import bson


class FeedHistorysApi(Resource):
    def get(self):
        # init FeedHistory objects
        objects = FeedHistory.objects()
        # add filter in this section

        # filter section
        # empty list for response
        response = []
        # access one feedhistory in objects
        for feedhistory in objects:
            # convert to dict
            feedhistory = feedhistory.to_mongo()
            # get pond and convert to dict
            pond = Pond.objects.get(
                id=str(feedhistory['pond_id'])).to_mongo()
            # get feedtype and convert to dict
            feedtype = FeedType.objects.get(
                id=str(feedhistory['feed_type_id'])).to_mongo()
            # resturcture response
            feedhistory.pop('pond_id')
            feedhistory.pop('feed_type_id')
            # add new key and value
            feedhistory["pond"] = pond
            feedhistory["feed_type"] = feedtype
            response.append(feedhistory)

        # dump json to json string
        response_dump = json.dumps(response, default=str)
        return Response(response_dump, mimetype="application/json", status=200)

    def post(self):
        body = request.get_json()
        # body["time_feeding"] = datetime.strptime(
        #     body["time_feeding"], '%Y-%m-%dT%H:%M:%SZ')
        # print(body)
        feedhistory = FeedHistory(**body).save()
        id = feedhistory.id
        return {'id': str(id)}, 200


class FeedHistoryApi(Resource):
    def put(self, id):
        body = request.get_json()
        body['updated_at'] = datetime.datetime.utcnow()
        FeedHistory.objects.get(id=id).update(**body)
        return '', 200

    def delete(self, id):
        feedhistory = FeedHistory.objects.get(id=id).delete()
        return '', 200

    def get(self, id):
        feedhistory = FeedHistory.objects.get(id=id).to_json()
        return Response(feedhistory, mimetype="application/json", status=200)

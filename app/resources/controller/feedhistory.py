from flask import Response, request
from app.database.models import FeedHistory, Pond
from flask_restful import Resource
import datetime


class FeedHistorysApi(Resource):
    def get(self):
        feedhistorys = FeedHistory.objects().to_json()
        # upgrade_feedhistorys = []
        # for logfeeding in feedhistorys:
        #     pond_id = int(logfeeding['pond_id']['$oid'])
        #     logfeeding['pond'] = TypeFeed.objects.get(id=pond_id).to_json()
        #     upgrade_feedhistorys.append(logfeeding)
        return Response(feedhistorys, mimetype="application/json", status=200)

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

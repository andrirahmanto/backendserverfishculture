from flask import Response, request
from app.database.models import FeedHistory, Pond, FeedType
from flask_restful import Resource
import datetime
import json


class FeedHistorysApi(Resource):
    def get(self):
        # init FeedHistory objects
        objects = FeedHistory.objects()
        # filter section

        # filter date
        # get args with default input "all"
        filter_date = request.args.get("filter_date", "all")
        # handle input "today"
        if filter_date == "today":
            start = datetime.datetime.today().replace(
                hour=0, minute=0, second=0, microsecond=0)
            end = start + datetime.timedelta(hours=24)
            date_query = {'created_at': {'$gte': start, '$lt': end}}
        # handle input "all"
        elif filter_date == "all":
            date_query = {}
        # handle input date with format like "2022-02-18"
        else:
            # convert string to datetime
            filter_date = datetime.datetime.strptime(filter_date, "%Y-%m-%d")
            start = filter_date
            end = start + datetime.timedelta(days=7)
            print(start)
            print(end)
            date_query = {'created_at': {'$gte': start, '$lt': end}}

        filter = objects.filter(__raw__=date_query)
        # empty list for response
        response = []
        # access one feedhistory in objects
        for feedhistory in filter:
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
        body = {
            "pond_id": request.form.get("pond_id", None),
            "feed_type_id": request.form.get("feed_type_id", None),
            "feed_dose": request.form.get("feed_dose", None)
        }
        feedhistory = FeedHistory(**body).save()
        id = feedhistory.id
        return {'id': str(id)}, 200


class FeedHistoryApi(Resource):
    def put(self, id):
        body = {
            "feed_dose": request.form.get("feed_dose", None),
            "updated_at": datetime.datetime.utcnow()
        }
        FeedHistory.objects.get(id=id).update(**body)
        return '', 200

    def delete(self, id):
        feedhistory = FeedHistory.objects.get(id=id).delete()
        return '', 200

    def get(self, id):
        objects = FeedHistory.objects.get(id=id)
        # convert to dict
        feedhistory = objects.to_mongo()
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
        response = json.dumps(feedhistory, default=str)
        return Response(response, mimetype="application/json", status=200)

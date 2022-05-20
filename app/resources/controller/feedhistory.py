from flask import Response, request
from app.database.models import FeedHistory, Pond, FeedType
from flask_restful import Resource
from app.database.db import db
import datetime
import json
from bson.json_util import dumps


class FeedHistorysApi(Resource):
    def get(self):
        try:
            # filter date
            # get args with default input "all"
            filter_date = request.args.get("filter_date", "all")
            # handle input "today"
            if filter_date == "today":
                date = datetime.datetime.today().strftime('%Y-%m-%d')
                date_equation = {'$eq': [date, {'$dateToString': {
                    'format': "%Y-%m-%d", 'date': "$feed_history_time"}}]}
            # handle input "all"
            elif filter_date == "all":
                date_equation = {}
            # handle input date with format like "2022-02-18"
            else:
                # convert string to datetime
                filter_date = datetime.datetime.strptime(
                    filter_date, "%Y-%m-%d")
                date_equation = {'$eq': [date, {'$dateToString': {
                    'format': "%Y-%m-%d", 'date': "$feed_history_time"}}]}

            pipeline = [
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$and': [{'$eq': ['$_id', '$$pondid']}]}}},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'pond'
                }},
                {'$lookup': {
                    'from': 'feed_type',
                    'let': {"feedid": "$feed_type_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$feedid']}}},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'feed_type'
                }},
                {"$project": {
                    "pond_id": 0,
                    "feed_type_id": 0,
                    "created_at": 0,
                    "updated_at": 0,
                }}
            ]
            feedhistory = FeedHistory.objects.aggregate(pipeline)
            list_feedhistory = list(feedhistory)
            response = json.dumps(list_feedhistory, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def post(self):
        try:
            body = {
                "pond_id": request.form.get("pond_id", None),
                "feed_type_id": request.form.get("feed_type_id", None),
                "feed_dose": request.form.get("feed_dose", None)
            }
            feedhistory = FeedHistory(**body).save()
            id = feedhistory.id
            return {'id': str(id), 'message': 'success input'}, 200
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryApi(Resource):
    def put(self, id):
        try:
            body = {
                "feed_dose": request.form.get("feed_dose", None),
                "updated_at": datetime.datetime.utcnow()
            }
            FeedHistory.objects.get(id=id).update(**body)
            response = {"message": "success"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def delete(self, id):
        try:
            feedhistory = FeedHistory.objects.get(id=id).delete()
            response = {"message": "success"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def get(self, id):
        try:
            feedhistory = FeedHistory.objects.get(id=id)
            pipline = [
                {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': id}]}}},
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$and': [{'$eq': ['$_id', '$$pondid']}]}}},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'pond'
                }},
                {'$lookup': {
                    'from': 'feed_type',
                    'let': {"feedid": "$feed_type_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$feedid']}}},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'feed_type'
                }},
                {"$project": {
                    "pond_id": 0,
                    "feed_type_id": 0,
                    "created_at": 0,
                    "updated_at": 0,
                }}
            ]
            print(id)
            feedhistory = FeedHistory.objects.aggregate(pipline)
            list_feedhistory = list(feedhistory)
            response = dict(list_feedhistory[0])
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryTodayByPond(Resource):
    def get(self):
        try:
            # make variable for default field
            default = datetime.datetime.today().strftime('%Y-%m-%d')
            # get args with default input today
            date = request.args.get("date", default)
            print(date)
            pipline = [
                {'$lookup': {
                    'from': 'feed_history',
                    'let': {"pondid": "$_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_id', '$$pondid']},
                            {'$eq': [date, {'$dateToString': {
                                'format': "%Y-%m-%d", 'date': "$feed_history_time"}}]}
                        ]}}},
                        {'$lookup': {
                            'from': 'feed_type',
                            'let': {"feedid": "$feed_type_id"},
                            'pipeline': [
                                {'$match': {
                                    '$expr': {'$eq': ['$_id', '$$feedid']}}},
                                {"$project": {
                                    "created_at": 0,
                                    "updated_at": 0,
                                }}
                            ],
                            'as': 'feed_type'
                        }},
                        {"$project": {
                            "_id": 1,
                            "feed_type_id": 1,
                            "feed_dose": 1,
                            "feed_history_time": 1,
                            "feed_type": 1,

                        }}
                    ],
                    'as': 'feed_historys_today'
                }},
                {"$project": {
                    "_id": 1,
                    "id_int": 1,
                    "alias": 1,
                    "location": 1,
                    "feed_historys_today": '$feed_historys_today',
                    "total_feed_dose_today": {"$sum": "$feed_historys_today.feed_dose"}
                }}
            ]
            ponds = Pond.objects().aggregate(pipline)
            response = list(ponds)
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryTodayByOnePond(Resource):
    def get(self, id):
        try:
            objects = Pond.objects.get(id=id)
            # make variable for default field
            default = datetime.datetime.today().strftime('%Y-%m-%d')
            # get args with default input today
            date = request.args.get("date", default)
            pipeline = [
                {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': id}]}}},
                {'$lookup': {
                    'from': 'feed_history',
                    'let': {"pondid": "$_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_id', '$$pondid']},
                            {'$eq': [date, {'$dateToString': {
                                'format': "%Y-%m-%d", 'date': "$feed_history_time"}}]}
                        ]}}},
                        {'$lookup': {
                            'from': 'feed_type',
                            'let': {"feedid": "$feed_type_id"},
                            'pipeline': [
                                {'$match': {
                                    '$expr': {'$eq': ['$_id', '$$feedid']}}},
                                {"$project": {
                                    "created_at": 0,
                                    "updated_at": 0,
                                }}
                            ],
                            'as': 'feed_type'
                        }},
                        {"$project": {
                            "_id": 1,
                            "feed_dose": 1,
                            "feed_history_time": 1,
                            "feed_type": 1,

                        }}
                    ],
                    'as': 'feed_historys_today'
                }},
                {"$project": {
                    "created_at": 0,
                    "updated_at": 0,
                }}
            ]
            data = Pond.objects.aggregate(pipeline)
            data = list(data)
            data = dict(data[0])
            response = json.dumps(data, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryMonthByPond(Resource):
    def get(self):
        try:
            # make variable for default field
            default = datetime.datetime.today().strftime('%Y-%m')
            # get args with default input today
            date = request.args.get("date", default)
            print(date)
            pipline = [
                {'$lookup': {
                    'from': 'feed_history',
                    'let': {"pondid": "$_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_id', '$$pondid']},
                            {'$eq': [date, {'$dateToString': {
                                'format': "%Y-%m", 'date': "$feed_history_time"}}]}
                        ]}}},
                    ],
                    'as': 'feed_historys_today'
                }},
                {"$project": {
                    "_id": 1,
                    "id_int": 1,
                    "alias": 1,
                    "location": 1,
                    "total_feed_historys": {"$size": "$feed_historys_today"},
                    "total_feed_dose": {"$sum": "$feed_historys_today.feed_dose"},
                    "avg_feed_dose": {'$avg': "$feed_historys_today.feed_dose"}
                }}
            ]
            ponds = Pond.objects().aggregate(pipline)
            response = list(ponds)
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

from flask import Response, request
from fishapi.database.models import FeedHistory, Pond, FeedType
from flask_restful import Resource
from fishapi.database.db import db
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
            pond_id = request.form.get("pond_id", None)
            feed_type_id = request.form.get("feed_type_id", None)
            body = {
                "pond_id": pond_id,
                "feed_type_id": feed_type_id,
                "feed_dose": request.form.get("feed_dose", None)
            }
            check_pond = Pond.objects.get(id=pond_id)
            check_feed_type = FeedType.objects.get(id=feed_type_id)
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
            body = request.form.to_dict(flat=True)
            FeedHistory.objects.get(id=id).update(**body)
            response = {"message": "success change data feedhistory", "id": id}
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
                {"$addFields": {
                    "pond": {"$first": "$pond"},
                    "feed_type": {"$first": "$feed_type"}
                }},
                {"$project": {
                    "pond_id": 0,
                    "feed_type_id": 0,
                    "created_at": 0,
                    "updated_at": 0,
                }}
            ]
            feedhistory = FeedHistory.objects.aggregate(pipline)
            list_feedhistory = list(feedhistory)
            response = dict(list_feedhistory[0])
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryByPond(Resource):
    def get(self):
        try:
            # Filter Date
            # DATE FIELD
            # make variable for default field
            default = datetime.datetime.today().strftime('%Y-%m-%d')
            # get args with default input today
            date = request.args.get("date", default)
            date = datetime.datetime.strptime(date, '%Y-%m-%d')  # datetime
            # RANGE FIELD
            # get args with default input daily
            date_range = request.args.get("range", "daily")
            if date_range == "monthly":
                month_format = '%Y-%m'
                month_date = date.strftime(month_format)
                date_query = {'$eq': [month_date, {'$dateToString': {
                    'format': month_format, 'date': "$feed_history_time"}}]}
            else:
                daily_format = '%Y-%m-%d'
                daily_date = date.strftime(daily_format)
                date_query = {'$eq': [daily_date, {'$dateToString': {
                    'format': daily_format, 'date': "$feed_history_time"}}]}
            # Filter Pond
            # LIST POND FIELD
            # make variable for default field
            list_pond = request.args.get("list_pond", default="[]")
            list_pond = json.loads(list_pond)
            list_pond_query = {}
            if len(list_pond) >= 1:
                list_pond_query = {"$match": {
                    "$expr": {"$in": [{"$toString": "$_id"}, list_pond]}}}
            pipline = [
                list_pond_query,
                {'$lookup': {
                    'from': 'feed_history',
                    'let': {"pondid": "$_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_id', '$$pondid']},
                            date_query
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
                        {"$addFields": {
                            "feed_type": {"$first": "$feed_type"}
                        }},
                        {"$project": {
                            "pond_id": 0,
                            "feed_type_id": 0,
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'feed_historys_list'
                }},
                {"$addFields": {
                    "total_feed_dose": {"$sum": "$feed_historys_list.feed_dose"},
                    "feed_historys_list": '$feed_historys_list'
                }},
                {"$project": {
                    "created_at": 0,
                    "updated_at": 0,
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


class FeedHistoryByOnePond(Resource):
    def get(self, id):
        try:
            objects = Pond.objects.get(id=id)
           # make variable for default field
            default = datetime.datetime.today().strftime('%Y-%m-%d')
            # get args with default input today
            date = request.args.get("date", default)
            date = datetime.datetime.strptime(date, '%Y-%m-%d')  # datetime
            # get args with default input daily
            date_range = request.args.get("range", "daily")
            if date_range == "monthly":
                month_format = '%Y-%m'
                month_date = date.strftime(month_format)
                date_query = {'$eq': [month_date, {'$dateToString': {
                    'format': month_format, 'date': "$feed_history_time"}}]}
            else:
                daily_format = '%Y-%m-%d'
                daily_date = date.strftime(daily_format)
                date_query = {'$eq': [daily_date, {'$dateToString': {
                    'format': daily_format, 'date': "$feed_history_time"}}]}
            pipeline = [
                {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': id}]}}},
                {'$lookup': {
                    'from': 'feed_history',
                    'let': {"pondid": "$_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_id', '$$pondid']},
                            date_query
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
                        {"$addFields": {
                            "feed_type": {"$first": "$feed_type"}
                        }},
                        {"$project": {
                            "pond_id": 0,
                            "feed_type_id": 0,
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'feed_historys_list'
                }},
                {"$addFields": {
                    "total_feed_dose": {"$sum": "$feed_historys_list.feed_dose"},
                    "feed_historys_list": '$feed_historys_list'
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

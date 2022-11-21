from flask import Response, request
from fishapi.database.models import *
from flask_restful import Resource
from fishapi.database.db import db
import datetime
import calendar
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
            print(pond_id)
            feed_type_id = request.form.get("feed_type_id", None)
            pond = Pond.objects.get(id=pond_id)
            if pond['isActive'] == False:
                response = {"message": "pond is not active"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            pond_activation = PondActivation.objects(
                pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
            feed_type = FeedType.objects.get(id=feed_type_id)
            feed_history_time = request.form.get("feed_history_time", None)
            if feed_history_time != None:
                feed_history_time = datetime.datetime.fromisoformat(
                    feed_history_time)
            body = {
                "pond_id": pond_id,
                "pond_activation_id": pond_activation.id,
                "feed_type_id": feed_type_id,
                "feed_dose": request.form.get("feed_dose", None),
                "feed_history_time": feed_history_time
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


class FeedHistoryMonthByActivation(Resource):

    def get(self, activation_id):
        try:
            pipeline = [
                {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_activation_id', {
                                '$toObjectId': activation_id}]},
                            ]}}},
                {"$addFields": {
                    "month": {"$month": "$feed_history_time"},
                    "year": {"$year": "$feed_history_time"},
                }},
                {"$group": {
                    "_id": "$month",
                    "year": {"$first": "$year"},
                    "total_feed": {"$sum": "$feed_dose"},
                    "total_feedhistory": {"$sum": 1}
                }},
                {"$sort": {"year": 1, "_id": 1}},
            ]
            feedHistorys = FeedHistory.objects.aggregate(pipeline)
            response = list(feedHistorys)
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryWeekByActivation(Resource):

    def get(self, activation_id, month):
        try:
            # get weeks
            weeks = []
            dateStart = datetime.datetime.strptime(month, "%Y-%m")
            daysInMonth = calendar.monthrange(
                dateStart.year, dateStart.month)[1]
            daysDelta = datetime.timedelta(days=daysInMonth)
            dateEnd = dateStart + daysDelta
            for i in range(daysInMonth+1):
                day = dateStart + datetime.timedelta(days=i)
                week = day.strftime("%W")
                if int(week) not in weeks:
                    weeks.append(int(week))
            print(weeks)
            pipeline = [
                {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_activation_id', {
                                '$toObjectId': activation_id}]},
                            {"$in": [{"$week": "$feed_history_time"}, weeks]},
                            ]}}},
                {"$addFields": {
                    "week": {"$week": "$feed_history_time"},
                    "month": {"$month": "$feed_history_time"},
                    "year": {"$year": "$feed_history_time"},
                }},
                {"$group": {
                    "_id": "$week",
                    "month": {"$first": "$month"},
                    "year": {"$first": "$year"},
                    "total_feed": {"$sum": "$feed_dose"},
                    "total_feedhistory": {"$sum": 1}
                }},
                {"$sort": {"year": 1, "_id": 1}},
            ]
            feedHistorys = FeedHistory.objects.aggregate(pipeline)
            response = list(feedHistorys)
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryDayByActivation(Resource):

    def get(self, activation_id, week):
        try:
            pipeline = [
                {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_activation_id', {
                                '$toObjectId': activation_id}]},
                            {"$eq": [
                                {"$week": "$feed_history_time"}, int(week)]},
                            ]}}},
                {"$addFields": {
                    "week": {"$week": "$feed_history_time"},
                    "day": {"$dayOfMonth": "$feed_history_time"},
                    "month": {"$month": "$feed_history_time"},
                    "year": {"$year": "$feed_history_time"},
                }},
                {"$group": {
                    "_id": "$day",
                    "month": {"$first": "$month"},
                    "year": {"$first": "$year"},
                    "total_feed": {"$sum": "$feed_dose"},
                    "total_feedhistory": {"$sum": 1}
                }},
                {"$sort": {"year": 1, "month": 1, "_id": 1}},
            ]
            feedHistorys = FeedHistory.objects.aggregate(pipeline)
            response = list(feedHistorys)
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryHourByActivation(Resource):

    def get(self, activation_id, day):
        try:
            pipeline = [
                {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_activation_id', {
                                '$toObjectId': activation_id}]},
                            {"$eq": [
                                {'$dateToString': {
                                    'format': "%Y-%m-%d", 'date': "$feed_history_time"}}, day]},
                            ]}}},
                {"$addFields": {
                    "week": {"$week": "$feed_history_time"},
                    "day": {"$dayOfMonth": "$feed_history_time"},
                    "month": {"$month": "$feed_history_time"},
                    "year": {"$year": "$feed_history_time"},
                }},
                {"$sort": {"year": 1, "month": 1, "_id": 1}},
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
            ]
            feedHistorys = FeedHistory.objects.aggregate(pipeline)
            response = list(feedHistorys)
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

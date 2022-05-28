from flask import Flask, render_template, url_for
from .database.db import initialize_db
from flask_restful import Api
from fishapi.database.models import FeedHistory, Pond, FeedType
from .resources.routes import initialize_routes
import json
from datetime import datetime


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    api = Api(app)
    app.config.from_pyfile('settings.cfg', silent=False)

    initialize_db(app)
    initialize_routes(api)

    @app.route('/')
    def home():
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
            # custom datetime

            # customdate = datetime.strptime(
            #     feedhistory['feed_history_time'], 'YYYY-MM-DD HH:MM:SS.mmmmmm')
            feedhistory['feed_history_time'] = feedhistory['feed_history_time'].strftime(
                "%a || %d-%B-%Y || %H.%M.%f")
        return render_template('home.html', name='Andri', feedhistorys=enumerate(response, start=1))

    @app.route('/feedhistory/today/', defaults={'date': datetime.today().strftime('%Y-%m-%d')})
    @app.route('/feedhistory/today/<date>')
    def feedhistoryToday(date):
        print(date)
        if len(date) > 7:
            format_date = '%Y-%m-%d'
        else:
            format_date = '%Y-%m'
        print(format_date)
        pipline = [
            {'$lookup': {
                'from': 'feed_history',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                        {'$eq': [date, {'$dateToString': {
                            'format': format_date, 'date': "$feed_history_time"}}]}
                    ]}}},
                    {'$lookup': {
                        'from': 'feed_type',
                        'let': {"feedid": "$feed_type_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$_id', '$$feedid']}}},
                        ],
                        'as': 'feed_type'
                    }},
                    {"$addFields": {
                        "feed_history_date": {'$dateToString': {
                            'format': "%d-%m-%Y", 'date': "$feed_history_time"}},
                        "feed_history_time": {'$dateToString': {
                            'format': "%H:%M:%S", 'date': "$feed_history_time"}},
                        "feed_type": {"$first": "$feed_type"}
                    }}
                ],
                'as': 'feed_historys_list'
            }},
            {"$addFields": {
                "total_feed_dose": {"$sum": "$feed_historys_list.feed_dose"},
            }}
        ]
        ponds = Pond.objects().aggregate(pipline)
        response = list(ponds)
        return render_template('today.html', name='Andri', ponds=enumerate(response, start=1))

    @app.route('/feedhistory/month')
    def feedhistoryMonth():
        # make variable for default field
        date = datetime.today().strftime('%Y-%m')
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
        print(response)
        return render_template('month.html', name='Andri', ponds=enumerate(response, start=1))

    return app

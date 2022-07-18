import os
from flask import Flask, render_template, url_for, current_app, Response
from .database.db import initialize_db
from flask_restful import Api
from fishapi.database.models import FeedHistory, Pond, FeedType, PondActivation, FishDeath
from .resources.helper import *
from .resources.routes import initialize_routes
import json
from datetime import datetime


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    api = Api(app)
    app.config.from_pyfile('settings.cfg', silent=False)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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
        return render_template('feedhistory/log.html', name='Andri', feedhistorys=enumerate(response, start=1))

    @app.route('/feedhistorys/daily/', defaults={'date': datetime.today().strftime('%Y-%m-%d')})
    @app.route('/feedhistorys/daily/<date>')
    def feedhistoryDaily(date):
        if len(date) > 7:
            format_date = '%Y-%m-%d'
        else:
            format_date = '%Y-%m'
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
        return render_template('feedhistory/daily.html', name='Andri', ponds=enumerate(response, start=1), date=date)

    @app.route('/feedhistorys/monthly/', defaults={'date': datetime.today().strftime('%Y-%m')})
    @app.route('/feedhistorys/monthly/<date>')
    def feedhistoryMonthly(date):
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
        date_read = reformatStringDate(date, '%Y-%m', '%B %Y')
        return render_template('feedhistory/monthly.html', name='Andri', ponds=enumerate(response, start=1), date=date, date_read=date_read)

    @app.route('/feedhistorys/monthly/detail/<pondid>/<date>')
    def feedhistoryMonthlyOnePond(pondid, date=datetime.today().strftime('%Y-%m')):
        # date = datetime.today().strftime('%Y-%m')
        pipeline = [
            {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': pondid}]}}},
            {'$lookup': {
                'from': 'feed_history',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                        {'$eq': [date, {'$dateToString': {
                            'format': '%Y-%m', 'date': "$feed_history_time"}}]}
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
                        "feed_history_date": {'$dateToString': {
                            'format': "%d-%m-%Y", 'date': "$feed_history_time"}},
                        "feed_history_time": {'$dateToString': {
                            'format': "%H:%M:%S", 'date': "$feed_history_time"}},
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
                "avg_feed_dose": {'$avg': "$feed_historys_list.feed_dose"},
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
        date_read = reformatStringDate(date, '%Y-%m', '%B %Y')
        return render_template('feedhistory/detail.html', name='Andri', pond=data, date=date, date_read=date_read)

    @app.route('/ponds')
    def pondView():
        pipeline = [
            {"$addFields": {
                "area": {"$cond": {
                    "if": {"$eq": ["$shape", "persegi"]},
                    "then": {"$multiply": ["$length", "$width"]},
                    "else": {"$round": [{"$divide": [
                        {"$multiply": [22, "$diameter", "$diameter"]},
                        28
                    ]}, 3]},
                }}
            }},
            {"$addFields": {
                "volume": {"$multiply": ["$area", "$height"]},
                "build_at":{'$dateToString': {
                    'format': "%d-%m-%Y", 'date': "$build_at"}}
            }},
            {"$project": {
                "pond_id": 0,
                "feed_type_id": 0,
                "created_at": 0,
                "updated_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipeline)
        response = list(ponds)
        return render_template('pond/pondlist.html', name='Andri', ponds=enumerate(response, start=1))

    @app.route('/ponds/activation')
    def pondActivationListView():
        pipeline = [
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                    ]}}},
                    {'$lookup': {
                        'from': 'water_preparation',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id', '$$pond_activation_id']}}},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                        'as': 'water_preparation'
                    }},
                    {"$addFields": {
                        "water_preparation": {"$first": "$water_preparation"}
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_type_id": 0,
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'pond_activation_list'
            }},
            {"$addFields": {
                "total_activation": {"$size": "$pond_activation_list"},
            }},
            {"$project": {
                "location": 0,
                "shape": 0,
                "material": 0,
                "length": 0,
                "width": 0,
                "diameter": 0,
                "height": 0,
                "image_name": 0,
                "pond_activation_list": 0,
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipeline)
        response = list(ponds)
        return render_template('pond/pondlist_active.html', name='Andri', ponds=enumerate(response, start=1))

    @app.route('/ponds/activation/<pondid>')
    def pondActivationView(pondid):
        pipeline = [
            {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': pondid}]}}},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                    ]}}},
                    {"$sort": {"activated_at": -1}},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'activation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                        'as': 'fish'
                    }},
                    {'$lookup': {
                        'from': 'water_preparation',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id', '$$pond_activation_id']}}},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                        'as': 'water_preparation'
                    }},
                    {"$addFields": {
                        "activated_at": {'$dateToString': {
                            'format': "%d-%m-%Y", 'date': "$activated_at"}},
                        "deactivated_at": {'$dateToString': {
                            'format': "%d-%m-%Y", 'date': "$deactivated_at"}},
                        "water_preparation": {"$first": "$water_preparation"}
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_type_id": 0,
                        "created_at": 0,
                        "updated_at": 0,
                    }},
                ],
                'as': 'pond_activation_list'
            }},
            {"$addFields": {
                "water_level": {"$round": ["$water_level", 3]},
                "pond_activation_list": "$pond_activation_list",
                "total_activation": {"$size": "$pond_activation_list"},
            }},
            {"$project": {
                "location": 0,
                "shape": 0,
                "material": 0,
                "length": 0,
                "width": 0,
                "diameter": 0,
                "height": 0,
                "image_name": 0,
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipeline)
        ponds = list(ponds)
        pond = dict(ponds[0])
        activations = enumerate(pond['pond_activation_list'], start=1)
        return render_template('pond/activationlist.html', name='Andri', pond=pond, activations=activations)

    @app.route('/ponds/activation/detail/<activationid>')
    def pondActivationDetailView(activationid):
        pondactivation = PondActivation.objects.get(id=activationid)
        pondactivation = pondactivation.to_mongo()
        pond_id = pondactivation["pond_id"]
        print(pond_id)
        pipeline = [
            {'$match': {
                '$expr': {'$eq': ['$_id', {'$toObjectId': pond_id}]}}},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                        {'$eq': ['$_id', {'$toObjectId': activationid}]},
                    ]}}},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'activation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                        'as': 'fish'
                    }},
                    {'$lookup': {
                        'from': 'water_preparation',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id', '$$pond_activation_id']}}},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                        'as': 'water_preparation'
                    }},
                    {"$addFields": {
                        "activated_at": {'$dateToString': {
                            'format': "%d-%m-%Y", 'date': "$activated_at"}},
                        "deactivated_at": {'$dateToString': {
                            'format': "%d-%m-%Y", 'date': "$deactivated_at"}},
                        "water_preparation": {"$first": "$water_preparation"}
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_type_id": 0,
                        "created_at": 0,
                        "updated_at": 0,
                    }},
                ],
                'as': 'pond_activation_list'
            }},
            {"$addFields": {
                "water_level": {"$round": ["$water_level", 3]},
                "pond_activation": {"$first": "$pond_activation_list"},
                "total_activation": {"$size": "$pond_activation_list"},
            }},
            {"$project": {
                "location": 0,
                "shape": 0,
                "material": 0,
                "length": 0,
                "width": 0,
                "diameter": 0,
                "height": 0,
                "image_name": 0,
                "pond_activation_list": 0,
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipeline)
        ponds = list(ponds)
        pond = dict(ponds[0])
        return render_template('pond/activationdetail.html', name='Andri', pond=pond)

    @app.route('/fishdeaths/', defaults={'date': datetime.today().strftime('%Y-%m')})
    @app.route('/fishdeaths/<date>')
    def fishDeathRecap(date):
        url = url_for('fishdeathimageapidummy', _external=True)
        format_date = "%Y-%m"
        pipline = [
            {"$match": {"$expr":
                        {'$eq': [date, {'$dateToString': {
                            'format': format_date, 'date': "$created_at"}}]}
                        }},
            {"$sort": {"created_at": -1}},
            {'$lookup': {
                'from': 'pond',
                        'let': {"pondid": "$pond_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$_id', '$$pondid']}}},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                'as': 'pond_list'
            }},
            {"$addFields": {
                "pond": {"$first": "$pond_list"},
                "date": {'$dateToString': {
                    'format': "%d-%m-%Y", 'date': "$created_at"}},
                "time": {'$dateToString': {
                    'format': "%H:%M", 'date': "$created_at"}},
                "image_link": {"$concat": [url, "/", {"$toString": "$_id"}]}
            }},
            {"$project": {
                "pond_list": 0
            }}
        ]
        fishdeaths = FishDeath.objects().aggregate(pipline)
        fishdeaths = list(fishdeaths)
        date_read = reformatStringDate(date, '%Y-%m', '%B %Y')
        # response = json.dumps(fishdeaths, default=str)
        # return Response(response, mimetype="application/json", status=200)
        return render_template('fishdeath/monthly.html', name='Andri', fishdeaths=enumerate(fishdeaths, start=1), date=date, date_read=date_read)

    @app.route('/ponds/fish')
    def pondFishView():
        pipeline = [
            {'$match': {'$expr': {'$eq': ['$isFinish', False]}}},
            {'$lookup': {
                'from': 'pond',
                'let': {"pondid": "$pond_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$eq': ['$_id', '$$pondid']}}},
                ],
                'as': 'pond_list'
            }},
            {"$addFields": {
                "activation_date": {'$dateToString': {
                    'format': "%d-%m-%Y", 'date': "$activated_at"}},
                "pond": {"$first": "$pond_list"}
            }},
            {"$project": {
                "pond_list": 0,
                "created_at": 0,
                "updated_at": 0,
            }},
            {'$lookup': {
                'from': 'fish_death',
                'let': {"activationid": "$_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$eq': ['$pond_activation_id', '$$activationid']}}},
                    {'$unwind': "$fish_death_amount"},
                    {"$addFields": {
                        "type": "$fish_death_amount.type",
                        "amount": "$fish_death_amount.amount"
                    }},
                    {"$project": {
                        "fish_death_amount": 0,
                    }},
                    {"$group": {
                        "_id": "$type",
                        "type": {"$first": "$type"},
                        "amount": {"$sum": "$amount"}
                    }},
                    {"$project": {
                        "_id": 0,
                    }},
                ],
                'as': 'fishdeath_recap'
            }},
            {"$addFields": {
                "total_fish_stock": {"$sum": "$fish.amount"},
                "total_fish_death": {"$sum": "$fishdeath_recap.amount"}
            }},
        ]
        pondactivations = PondActivation.objects().aggregate(pipeline)
        pondactivations = list(pondactivations)
        for pondactivation in pondactivations:
            fishtype_list = list()
            for index in range(len(pondactivation['fish'])):
                fishtype_list.append(pondactivation['fish'][index]["type"])
            list1 = pondactivation['fish']
            list2 = pondactivation['fishdeath_recap']
            list3 = []
            for typefish in fishtype_list:
                obj = getAmountFishByType(typefish, list1)
                obj2 = getAmountFishByType(typefish, list2)
                print(obj2)
                data = {
                    "type": typefish,
                    "amount": obj - obj2
                }
                list3.append(data)
            pondactivation["fish_alive"] = list3
        # response = json.dumps(pondactivations, default=str)
        # return Response(response, mimetype="application/json", status=200)
        pondactivations = enumerate(pondactivations, start=1)
        return render_template('pond/fish.html', name='Andri', pondactivations=pondactivations)

    return app

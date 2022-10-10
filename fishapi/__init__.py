import os
from flask import Flask, render_template, url_for, current_app, Response
from .database.db import initialize_db
from flask_restful import Api
from fishapi.database.models import FeedHistory, Pond, FeedType, PondActivation, FishDeath, FishTransfer, FishGrading, OptionTable, DailyWaterQuality, WeeklyWaterQuality, PondTreatment
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
        pipeline = [
            {'$lookup': {
                'from': 'pond',
                'let': {"pondid": "$pond_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                    {"$project": {
                        "_id": 1,
                        "alias": 1,
                        "location": 1,
                        "build_at": 1,
                        "isActive": 1,
                    }}
                ],
                'as': 'pond'
            }},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"activationid": "$pond_activation_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$eq': ['$_id', '$$activationid']}}},
                    {"$addFields": {
                        "activation_date": {'$dateToString': {
                            'format': "%d-%m-%Y", 'date': "$activated_at"}},
                    }},
                    {"$project": {
                        "_id": 1,
                        "id_int": 1,
                        "isFinish": 1,
                        "isWaterPreparation": 1,
                        "water_level": 1,
                        "activated_at": 1,
                        "activation_date": 1
                    }}
                ],
                'as': 'pond_activation'
            }},
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
                "pond": {"$first": "$pond"},
                "pond_activation": {"$first": "$pond_activation"},
                "feed_type": {"$first": "$feed_type"},
                "date": {'$dateToString': {
                    'format': "%d-%m-%Y", 'date': "$feed_history_time"}},
                "time": {'$dateToString': {
                    'format': "%H:%M", 'date': "$feed_history_time"}},
            }},
            {"$project": {
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        feedhistorys = FeedHistory.objects.aggregate(pipeline)
        response = list(feedhistorys)
        # response = json.dumps(response, default=str)
        # return Response(response, mimetype="application/json", status=200)
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
        return render_template('pond/activationlist.html', name='Andri', pond=pond, activations=activations, len_activation=len(pond['pond_activation_list']))

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
                'from': 'fish_log',
                'let': {"fish_death_id": "$_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$and': [
                            {'$eq': ['$fish_death_id',
                                     '$$fish_death_id']},
                            {'$eq': ['$type_log',
                                     'death']},
                        ]}
                    }},
                    {"$project": {
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'fish'
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
                'from': 'fish_log',
                'let': {"pond_activation_id": "$_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$and': [
                            {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                            {'$eq': ['$type_log',
                                     'activation']},
                        ]}
                    }},
                    {"$project": {
                        "created_at": 0,
                        "updated_at": 0,
                    }},
                    {"$group": {
                        "_id": "$fish_type",
                        "fish_type": {"$first": "$fish_type"},
                        "fish_amount": {"$sum": "$fish_amount"}
                    }},
                    {"$sort": {"fish_type": -1}},
                    {"$project": {
                        "_id": 0,
                    }},
                ],
                'as': 'fish_stock'
            }},
            {'$lookup': {
                'from': 'fish_log',
                'let': {"pond_activation_id": "$_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$and': [
                            {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                            {'$eq': ['$type_log',
                                     'death']},
                        ]}
                    }},
                    {"$project": {
                        "created_at": 0,
                        "updated_at": 0,
                    }},
                    {"$group": {
                        "_id": "$fish_type",
                        "fish_type": {"$first": "$fish_type"},
                        "fish_amount": {"$sum": "$fish_amount"}
                    }},
                    {"$sort": {"fish_type": -1}},
                    {"$project": {
                        "_id": 0,
                    }},
                ],
                'as': 'fish_death_recap'
            }},
            {'$lookup': {
                'from': 'fish_log',
                'let': {"pond_activation_id": "$_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$and': [
                            {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                        ]}
                    }},
                    {"$project": {
                        "created_at": 0,
                        "updated_at": 0,
                    }},
                    {"$group": {
                        "_id": "$fish_type",
                        "fish_type": {"$first": "$fish_type"},
                        "fish_amount": {"$sum": "$fish_amount"}
                    }},
                    {"$sort": {"fish_type": -1}},
                    {"$project": {
                        "_id": 0,
                    }},
                ],
                'as': 'fish_in_pond'
            }},
            {'$lookup': {
                'from': 'fish_log',
                'let': {"pond_activation_id": "$_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$and': [
                            {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                            {'$eq': ['$type_log',
                                     'transfer_out']},
                        ]}
                    }},
                    {"$project": {
                        "created_at": 0,
                        "updated_at": 0,
                    }},
                    {"$group": {
                        "_id": "$fish_type",
                        "fish_type": {"$first": "$fish_type"},
                        "fish_amount": {"$sum": "$fish_amount"}
                    }},
                    {"$sort": {"fish_type": -1}},
                    {"$project": {
                        "_id": 0,
                    }},
                ],
                'as': 'fish_transfer_out'
            }},
            {'$lookup': {
                'from': 'fish_log',
                'let': {"pond_activation_id": "$_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$and': [
                            {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                            {'$eq': ['$type_log',
                                     'transfer_in']},
                        ]}
                    }},
                    {"$project": {
                        "created_at": 0,
                        "updated_at": 0,
                    }},
                    {"$group": {
                        "_id": "$fish_type",
                        "fish_type": {"$first": "$fish_type"},
                        "fish_amount": {"$sum": "$fish_amount"}
                    }},
                    {"$sort": {"fish_type": -1}},
                    {"$project": {
                        "_id": 0,
                    }},
                ],
                'as': 'fish_transfer_in'
            }},
            {"$addFields": {
                "total_fish_stock": {"$sum": "$fish_stock.fish_amount"},
                "total_fish_death": {"$sum": "$fish_death_recap.fish_amount"},
                "total_fish_in_pond": {"$sum": "$fish_in_pond.fish_amount"},
                "total_fish_transfer_out": {"$sum": "$fish_transfer_out.fish_amount"},
                "total_fish_transfer_in": {"$sum": "$fish_transfer_in.fish_amount"},
            }},
        ]
        pondactivations = PondActivation.objects().aggregate(pipeline)
        pondactivations = list(pondactivations)
        # response = json.dumps(pondactivations, default=str)
        # return Response(response, mimetype="application/json", status=200)
        pondactivations = enumerate(pondactivations, start=1)
        return render_template('pond/fish.html', name='Andri', pondactivations=pondactivations)

    @app.route('/fishtransfers/', defaults={'date': datetime.today().strftime('%Y-%m')})
    @app.route('/fishtransfers/<date>')
    def fishTransferRecap(date):
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
                'let': {"pondid": "$origin_pond_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$eq': ['$_id', '$$pondid']}}},
                    {"$project": {
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'origin_pond'
            }},
            {'$lookup': {
                'from': 'pond',
                'let': {"pondid": "$destination_pond_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$eq': ['$_id', '$$pondid']}}},
                    {"$project": {
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'destination_pond'
            }},
            {"$addFields": {
                "origin_pond": {"$first": "$origin_pond"},
                "destination_pond": {"$first": "$destination_pond"},
            }},
            {'$lookup': {
                'from': 'fish_log',
                'let': {"fish_transfer_id": "$_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$and': [
                            {'$eq': ['$fish_transfer_id',
                                     '$$fish_transfer_id']},
                            {'$eq': ['$type_log',
                                     'transfer_out']},
                        ]}
                    }},
                    {"$project": {
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'fish'
            }},
            {"$addFields": {
                "date": {'$dateToString': {
                    'format': "%d-%m-%Y %H:%M", 'date': "$created_at"}},
            }},
            {"$project": {
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        fishtransfers = FishTransfer.objects().aggregate(pipline)
        fishtransfers = list(fishtransfers)
        date_read = reformatStringDate(date, '%Y-%m', '%B %Y')
        # response = json.dumps(fishtransfers, default=str)
        # return Response(response, mimetype="application/json", status=200)
        return render_template('fishtransfer/monthly.html', name='Andri', fishtransfers=enumerate(fishtransfers, start=1), date=date, date_read=date_read)

    @app.route('/fishgradings/', defaults={'date': datetime.today().strftime('%Y-%m')})
    @app.route('/fishgradings/<date>')
    def fishGradingRecap(date):
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
                    {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                    {"$project": {
                        "_id": 1,
                        "alias": 1,
                        "location": 1,
                        "build_at": 1,
                        "isActive": 1,
                    }}
                ],
                'as': 'pond'
            }},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"activationid": "$pond_activation_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$eq': ['$_id', '$$activationid']}}},
                    {"$addFields": {
                        "date": {'$dateToString': {
                            'format': "%d-%m-%Y", 'date': "$activated_at"}},
                    }},
                    {"$project": {
                        "_id": 1,
                        "isFinish": 1,
                        "isWaterPreparation": 1,
                        "constanta_oversize": 1,
                        "constanta_undersize": 1,
                        "water_level": 1,
                        "activated_at": 1,
                        "date": 1,
                    }}
                ],
                'as': 'pond_activation'
            }},
            {"$addFields": {
                "date": {'$dateToString': {
                    'format': "%d-%m-%Y", 'date': "$created_at"}},
                "pond": {"$first": "$pond"},
                "pond_activation": {"$first": "$pond_activation"},
            }},
            {"$addFields": {
                "date": {'$dateToString': {
                    'format': "%d-%m-%Y", 'date': "$created_at"}},
                "constanta_oversize": "$pond_activation.constanta_oversize",
                "constanta_undersize": "$pond_activation.constanta_undersize",
            }},
            {"$project": {
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        fishgradings = FishGrading.objects.aggregate(pipline)
        fishgradings = list(fishgradings)
        date_read = reformatStringDate(date, '%Y-%m', '%B %Y')
        link_graph = url_for('api.graph', _external=True)
        # response = json.dumps(fishgradings, default=str)
        # return Response(response, mimetype="application/json", status=200)
        return render_template('fishgrading/monthly.html', name='Andri', fishgradings=enumerate(fishgradings, start=1), date=date, date_read=date_read, link_graph=link_graph)

    @app.route('/getoption/')
    def getOption():
        body = {
            "type": "pond/shape",
            "option": str(["bundar", "persegi"])
        }
        optiontable_list = OptionTable(**body).save()
        return

    @app.route('/dailywaterquality/', defaults={'date': datetime.today().strftime('%Y-%m')})
    @app.route('/dailywaterquality/<date>')
    def dailyWaterQualityRecap(date):
        format_date = "%Y-%m"
        pipeline = [
            {'$match': {'$expr': {'$and': [
                        {'$eq': [date, {'$dateToString': {
                            'format': format_date, 'date': "$created_at"}}]},
                        ]
            }}},
            {"$sort": {"created_at": 1}},
            {'$lookup': {
                'from': 'pond',
                'let': {"pondid": "$pond_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                    {"$project": {
                        "_id": 1,
                        "alias": 1,
                        "location": 1,
                        "build_at": 1,
                        "isActive": 1,
                    }}
                ],
                'as': 'pond'
            }},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"activationid": "$pond_activation_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$eq': ['$_id', '$$activationid']}}},
                    {"$addFields": {
                        "activation_date": {'$dateToString': {
                            'format': "%d-%m-%Y", 'date': "$activated_at"}},
                    }},
                    {"$project": {
                        "_id": 1,
                        "id_int": 1,
                        "isFinish": 1,
                        "isWaterPreparation": 1,
                        "water_level": 1,
                        "activated_at": 1,
                        "activation_date": 1
                    }}
                ],
                'as': 'pond_activation'
            }},
            {"$addFields": {
                "pond": {"$first": "$pond"},
                "pond_activation": {"$first": "$pond_activation"},
                "date": {'$dateToString': {
                    'format': "%d-%m-%Y", 'date': "$created_at"}},
                "ph_desc": {
                    "$switch":
                    {
                        "branches": [
                            {
                                "case": {"$lt": ["$ph", 6]},
                                "then": "berbahaya"
                            },
                            {
                                "case": {"$gt": ["$ph", 8]},
                                "then": "berbahaya"
                            }
                        ],
                        "default": "normal"
                    }
                },
                "do_desc": {
                    "$switch":
                    {
                        "branches": [
                            {
                                "case": {"$or": [
                                    {"$lt": ["$do", 3]},
                                    {"$gt": ["$do", 7.5]}
                                ]},
                                "then": "berbahaya"
                            },
                            {
                                "case": {"$or": [
                                    {"$and": [{"$gte": ["$do", 3]}, {
                                        "$lte": ["$do", 4]}]},
                                    {"$and": [{"$gt": ["$do", 6]}, {
                                        "$lte": ["$do", 7.5]}]}
                                ]},
                                "then": "semi berbahaya"
                            }
                        ],
                        "default": "normal"
                    }
                }
            }},
            {"$project": {
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        dailyquality_list = DailyWaterQuality.objects.aggregate(pipeline)
        dailyquality_list = list(dailyquality_list)
        date_read = reformatStringDate(date, '%Y-%m', '%B %Y')
        # response = json.dumps(dailyquality_list, default=str)
        # return Response(response, mimetype="application/json", status=200)
        return render_template('waterquality/daily.html', name='Andri', dailyquality_list=enumerate(dailyquality_list, start=1), date=date, date_read=date_read)

    @app.route('/weeklywaterquality/', defaults={'date': datetime.today().strftime('%Y-%m')})
    @app.route('/weeklywaterquality/<date>')
    def weeklyWaterQualityRecap(date):
        format_date = "%Y-%m"
        pipeline = [
            {'$match': {'$expr': {'$and': [
                        {'$eq': [date, {'$dateToString': {
                            'format': format_date, 'date': "$created_at"}}]},
                        ]
            }}},
            {"$sort": {"created_at": 1}},
            {'$lookup': {
                'from': 'pond',
                'let': {"pondid": "$pond_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                    {"$project": {
                        "_id": 1,
                        "alias": 1,
                        "location": 1,
                        "build_at": 1,
                        "isActive": 1,
                    }}
                ],
                'as': 'pond'
            }},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"activationid": "$pond_activation_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$eq': ['$_id', '$$activationid']}}},
                    {"$addFields": {
                        "activation_date": {'$dateToString': {
                            'format': "%d-%m-%Y", 'date': "$activated_at"}},
                    }},
                    {"$project": {
                        "_id": 1,
                        "id_int": 1,
                        "isFinish": 1,
                        "isWaterPreparation": 1,
                        "water_level": 1,
                        "activated_at": 1,
                        "activation_date": 1
                    }}
                ],
                'as': 'pond_activation'
            }},
            {"$addFields": {
                "pond": {"$first": "$pond"},
                "pond_activation": {"$first": "$pond_activation"},
                "date": {'$dateToString': {
                    'format': "%d-%m-%Y", 'date': "$created_at"}},
                "floc_desc": {
                    "$switch":
                    {
                        "branches": [
                            {"case": {
                                "$eq": ["$floc", "0-10"]}, "then": "pembentukan"},
                            {"case": {
                                "$eq": ["$floc", "11-30"]}, "then": "normal"},
                            {"case": {
                                "$eq": ["$floc", "31-50"]}, "then": "tebal"},
                            {"case": {
                                "$eq": ["$floc", "51-100"]}, "then": "abnormal"},
                            {"case": {
                                "$eq": ["$floc", "101-300"]}, "then": "berbahaya"},
                            {"case": {
                                "$eq": ["$floc", ">300"]}, "then": "deadzone"},
                        ],
                        "default": "normal"
                    }
                },
                "nitrite_desc": {
                    "$switch":
                    {
                        "branches": [
                            {"case": {
                                "$eq": ["$ammonia", 0]}, "then": "tidak ada"},
                            {"case": {
                                "$eq": ["$ammonia", 1]}, "then": "sedikit"},
                            {"case": {
                                "$eq": ["$ammonia", 5]}, "then": "aman"},
                            {"case": {
                                "$eq": ["$ammonia", 10]}, "then": "pekat"},
                            {"case": {
                                "$eq": ["$ammonia", 20]}, "then": "banyak"},
                            {"case": {
                                "$eq": ["$ammonia", 40]}, "then": "berbahaya"},
                            {"case": {
                                "$eq": ["$ammonia", 80]}, "then": "deadzone"},
                        ],
                        "default": "normal"
                    }
                },
                "nitrate_desc": {
                    "$switch":
                    {
                        "branches": [
                            {"case": {
                                "$eq": ["$ammonia", 0]}, "then": "tidak ada"},
                            {"case": {
                                "$eq": ["$ammonia", 10]}, "then": "sedikit"},
                            {"case": {
                                "$eq": ["$ammonia", 25]}, "then": "aman"},
                            {"case": {
                                "$eq": ["$ammonia", 50]}, "then": "pekat"},
                            {"case": {
                                "$eq": ["$ammonia", 100]}, "then": "banyak"},
                            {"case": {
                                "$eq": ["$ammonia", 250]}, "then": "berbahaya"},
                            {"case": {
                                "$eq": ["$ammonia", 500]}, "then": "deadzone"},
                        ],
                        "default": "normal"
                    }
                },
                "ammonia_desc": {
                    "$switch":
                    {
                        "branches": [
                            {"case": {
                                "$eq": ["$ammonia", 0]}, "then": "sedikit"},
                            {"case": {
                                "$eq": ["$ammonia", 0.25]}, "then": "aman"},
                            {"case": {
                                "$eq": ["$ammonia", 1.5]}, "then": "pekat"},
                            {"case": {
                                "$eq": ["$ammonia", 3]}, "then": "banyak"},
                            {"case": {
                                "$eq": ["$ammonia", 5]}, "then": "berbahaya"},
                        ],
                        "default": "normal"
                    }
                },
                "hardness_desc": {
                    "$switch":
                    {
                        "branches": [
                            {"case": {
                                "$eq": ["$ammonia", 0]}, "then": "sedikit"},
                            {"case": {
                                "$eq": ["$ammonia", 25]}, "then": "aman"},
                            {"case": {
                                "$eq": ["$ammonia", 50]}, "then": "pekat"},
                            {"case": {
                                "$eq": ["$ammonia", 125]}, "then": "banyak"},
                            {"case": {
                                "$eq": ["$ammonia", 250]}, "then": "berbahaya"},
                            {"case": {
                                "$eq": ["$ammonia", 425]}, "then": "deadzone"},
                        ],
                        "default": "normal"
                    }
                },
            }},
            {"$project": {
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        weeklyquality_list = WeeklyWaterQuality.objects.aggregate(pipeline)
        weeklyquality_list = list(weeklyquality_list)
        date_read = reformatStringDate(date, '%Y-%m', '%B %Y')
        # response = json.dumps(weeklyquality_list, default=str)
        # return Response(response, mimetype="application/json", status=200)
        return render_template('waterquality/weekly.html', name='Andri', weeklyquality_list=enumerate(weeklyquality_list, start=1), date=date, date_read=date_read)

    @app.route('/pondtreatment/', defaults={'date': datetime.today().strftime('%Y-%m')})
    @app.route('/pondtreatment/<date>')
    def pondTreatmentRecap(date):
        format_date = "%Y-%m"
        pipeline = [
            {'$match': {'$expr': {'$and': [
                        {'$eq': [date, {'$dateToString': {
                            'format': format_date, 'date': "$created_at"}}]},
                        ]
            }}},
            {"$sort": {"created_at": 1}},
            {'$lookup': {
                'from': 'pond',
                'let': {"pondid": "$pond_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                    {"$project": {
                        "_id": 1,
                        "alias": 1,
                        "location": 1,
                        "build_at": 1,
                        "isActive": 1,
                    }}
                ],
                'as': 'pond'
            }},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"activationid": "$pond_activation_id"},
                'pipeline': [
                    {'$match': {
                        '$expr': {'$eq': ['$_id', '$$activationid']}}},
                    {"$addFields": {
                        "activation_date": {'$dateToString': {
                            'format': "%d-%m-%Y", 'date': "$activated_at"}},
                    }},
                    {"$project": {
                        "_id": 1,
                        "id_int": 1,
                        "isFinish": 1,
                        "isWaterPreparation": 1,
                        "water_level": 1,
                        "activated_at": 1
                    }}
                ],
                'as': 'pond_activation'
            }},
            {"$addFields": {
                "pond": {"$first": "$pond"},
                "pond_activation": {"$first": "$pond_activation"},
                "date": {'$dateToString': {
                    'format': "%d-%m-%Y", 'date': "$created_at"}},
            }},
            {"$project": {
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        pondtreatments = PondTreatment.objects.aggregate(pipeline)
        pondtreatments = list(pondtreatments)
        date_read = reformatStringDate(date, '%Y-%m', '%B %Y')
        # response = json.dumps(pondtreatments, default=str)
        # return Response(response, mimetype="application/json", status=200)
        return render_template('pondtreatment/month.html', name='Andri', pondtreatments=enumerate(pondtreatments, start=1), date=date, date_read=date_read)

    return app

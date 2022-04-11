from flask import Flask, render_template, url_for
from .database.db import initialize_db
from flask_restful import Api
from app.database.models import FeedHistory
from .resources.routes import initialize_routes
from bson.json_util import dumps
import json
import datetime


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    api = Api(app)
    app.config.from_pyfile('settings.cfg', silent=False)
    # app.config['MONGODB_SETTINGS'] = {
    #     'db': 'fishapidb',
    #     'host': '127.0.0.1',
    #     'port': 27017
    # }

    initialize_db(app)
    initialize_routes(api)

    @app.route('/')
    def home():
        # data = FeedHistory.objects().to_json()
        # # feedhistory = feedhistorys[0].to_json()
        # data = json.loads(data)
        # date = data[0]["feed_history_time"]["$date"]
        # date_up = data[0]["feed_history_time"]["$date"]
        # print (type(date))
        datas = FeedHistory.objects()
        datas_list = []
        for data in datas:
            data_dict = data.to_mongo().to_dict()
            data_dict['created_at'] = data.created_at.isoformat()
            datas_list.append(data_dict)
        data = datas_list
        return render_template('home.html', name='Andri', feedhistorys=data)

    return app

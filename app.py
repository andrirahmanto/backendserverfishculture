from flask import Flask
from database.db import initialize_db
from flask_restful import Api
from resources.routes import initialize_routes

app = Flask(__name__)
api = Api(app)

app.config['MONGODB_SETTINGS'] = {
    'db': 'fishapidb',
    'host': '127.0.0.1',
    'port': 27017
}

initialize_db(app)
initialize_routes(api)

app.run()

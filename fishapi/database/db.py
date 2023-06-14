from flask_mongoengine import MongoEngine

db = MongoEngine()
alias_connection = 'v1connection'

def initialize_db(app):
    db.init_app(app)
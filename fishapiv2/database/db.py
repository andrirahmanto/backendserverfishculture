from flask_mongoengine import MongoEngine

db = MongoEngine()
alias_connection = 'new_connection'

def initialize_db(app):
    db.init_app(app)
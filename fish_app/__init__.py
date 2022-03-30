import os

from flask import Flask, render_template
from . import routes


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('settings.cfg', silent=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(routes.bp)

    @app.route('/index')
    @app.route('/')
    def index():
        """
        for any other routes than index please see routes blueprint
        """
        return render_template('index.html')

    @app.errorhandler(404)
    def page_not_found(e):
        # note that we set the 404 status explicitly
        return render_template('404.html'), 404

    return app

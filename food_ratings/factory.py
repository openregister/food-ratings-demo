# -*- coding: utf-8 -*-
'''The app module, containing the app factory function.'''
from flask import Flask, render_template

def asset_path_context_processor():
    return {'asset_path': '/static/'}

def create_app(config_filename):
    ''' An application factory, as explained here:
        http://flask.pocoo.org/docs/patterns/appfactories/
    '''
    app = Flask(__name__)
    app.config.from_object(config_filename)
    register_errorhandlers(app)
    register_blueprints(app)
    register_extensions(app)
    app.context_processor(asset_path_context_processor)
    return app

def register_errorhandlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template("{0}.html".format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None

def register_blueprints(app):
    from food_ratings.frontend.views import frontend
    app.register_blueprint(frontend)

def register_extensions(app):
    pass
    # from redis import Redis
    # import requests
    # import requests_cache
    # from urllib.parse import urlparse

    # redis_url = app.config.get('REDIS_URL')
    # if redis_url:
    #     url = urlparse(redis_url)
    #     cache = Redis(host=url.hostname, port=url.port, password=url.password)
    # else:
    #     cache = Redis() # local dev default

    # requests_cache.install_cache('registers_cache', backend='redis', expire_after=300, connection=cache)

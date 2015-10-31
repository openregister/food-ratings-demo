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
    register_filters(app)
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

def register_filters(app):

    def format_address(s):
        address_lines = []
        if s['property']:
            address_lines.append(s['property'])
        if s['street']:
            address_lines.append(s['street'])
        if s['town']:
            address_lines.append(s['town'])
        if s['postcode']:
            address_lines.append(s['postcode'])
        return ", ".join(address_lines)


    def format_inspection(s):
        ratings_map = {"0": "Urgent improvement needed", "1": "Major improvement needed", "2": "Improvement needed", "3": "Generally satisfactory", "4": "Good", "5": "Very good"}

        if s.get('last_inspection'):
            rating_value = s['last_inspection']['food_premises_rating_value']
        elif s.get('food_premises_rating_value'):
            rating_value = s['food_premises_rating_value']
        elif s.get('food-premises-rating-value'):
            rating_value = s['food-premises-rating-value']
        else:
            rating_value = "Awaiting Inspection"

        return "Rating: %s — %s" % (rating_value, ratings_map.get(rating_value, "Not yet known"))

    def format_curie(s):
        return s.split(":")[1]

    # TBD: translate markdown..
    def format_reply(s):
        return s.replace('\\n','<br/>\n').replace('\n', '<br/>')


    # def format_inspection_date(s):
    #     inspection_lines = []
    #     if s['last_inspection']:
    #         out = "Last inspection: %s" % s['last_inspection']['start_date']
    #         inspection_lines.append(out)
    #         out = "Rating: %s" % s['last_inspection']['food_premises_rating_value']
    #         inspection_lines.append(out)
    #     else:
    #         inspection_lines.append("Not inspected yet")

    #     return " ".join(inspection_lines)

    app.jinja_env.filters['format_address'] = format_address
    app.jinja_env.filters['format_inspection'] = format_inspection
    app.jinja_env.filters['format_curie'] = format_curie
    app.jinja_env.filters['format_reply'] = format_reply


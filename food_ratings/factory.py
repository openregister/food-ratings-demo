# -*- coding: utf-8 -*-
'''The app module, containing the app factory function.'''
from flask import Flask, render_template
import re
from datetime import datetime

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


    def format_rating(rating):
        ratings_map = {
            "0": "— Urgent improvement needed",
            "1": "— Major improvement needed",
            "2": "— Improvement needed",
            "3": "— Generally satisfactory",
            "4": "— Good",
            "5": "— Very good"
        }
        value = rating.get('food-premises-rating-value', 'Unknown')
        return "<strong>%s</strong> %s" % (value, ratings_map.get(value, ''))

    def format_register(entry, name=''):
        return '<a href="http://%s.prod.openregister.org/%s/%s">%s:%s</a>' % (
            name, name, entry[name], name, entry[name])

    def format_entry(entry, name=''):
        return entry

    def format_curie(s):
        return s.split(":")[1]

    # TBD: translate markdown..
    def format_reply(s):
        r = s.replace('\\n','<br/>\n').replace('\n', '<br/>')
        return re.sub('(<br/> *)+$', '', r)

    def format_date(d):
        try:
            return datetime.strptime(d, '%Y-%m-%d').strftime('%-d %B %Y')
        except Exception as e:
            return ''

    app.jinja_env.filters['format_address'] = format_address
    app.jinja_env.filters['format_rating'] = format_rating
    app.jinja_env.filters['format_curie'] = format_curie
    app.jinja_env.filters['format_reply'] = format_reply
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_register'] = format_register
    app.jinja_env.filters['format_entry'] = format_entry


# -*- coding: utf-8 -*-
'''The app module, containing the app factory function.'''
from flask import Flask, render_template
import re
from datetime import datetime
from .frontend.views import _config
from .frontend.views import _entry
from flask.ext.cache import Cache
import food_ratings.modules.caching as caching

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
    caching.init_cache(app)

def register_filters(app):
    def format_address(address_bundle):
        address_lines = []
        if address_bundle.get("address"):
            address_lines.append(address_bundle.get("address").get("name"))
        if address_bundle.get("street"):
            address_lines.append(address_bundle.get("street").get("name"))
        if address_bundle.get("place"):
            address_lines.append(address_bundle.get("place").get("name"))
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

    def format_rating_score(rating, field):
        score_map = {
            "30": "— Imminent and serious risks.",
            "25": "— Imminent and serious risks.",
            "20": "— Widespread and significant risks.",
            "15": "— Some significant risks.",
            "10": "— No unacceptable risks identified.",
            "5":  "— No risks identified.",
            "0":  "— No risks identified.",
        }
        value = rating.get(field, 'Unknown')
        return "<strong>%s</strong> %s" % (value, score_map.get(value, ''))

    def format_register(entry, name=''):
        return '<a href="%s/%s/%s">%s:%s</a>' % (
            _config(name, 'register'), name, entry[name], name, entry[name])

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
    app.jinja_env.filters['format_rating_score'] = format_rating_score
    app.jinja_env.filters['format_curie'] = format_curie
    app.jinja_env.filters['format_reply'] = format_reply
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_register'] = format_register
    app.jinja_env.filters['format_entry'] = format_entry


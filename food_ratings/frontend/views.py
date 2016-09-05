# -*- coding: utf-8 -*-
import requests, sys, os
sys.path.append('..')

from flask import (
    render_template,
    Blueprint,
    flash,
    abort,
    current_app,
    request,
    redirect,
    url_for,
    jsonify,
    json,
    make_response
)

from food_ratings.frontend.forms import SearchForm
from requests_futures.sessions import FuturesSession
from concurrent.futures import Future

import food_ratings.modules.caching as caching

frontend = Blueprint('frontend', __name__, template_folder='templates')

def _config(name, suffix):
    var = '%s_%s' % (name, suffix)
    var = var.upper().replace('-', '_')
    return current_app.config[var]


def _get(url, params=None):
    response = requests.get(url, params=params)
    current_app.logger.info("GET: %s [%s] %s" % (response.url, response.status_code, response.text))
    return response

# search index has '_' instead of '-' in field names ..
def _index(index, field, value, sortby=''):
    url = _config(index, 'search_url')
    params = {
        "q": value,
        "q.options": "{fields:['%s']}" % (field.replace('-', '_'))
    }

    if sortby:
        params['sort'] = '%s desc' % (sortby.replace('-', '_'))

    response = _get(url, params=params)
    results = [hit['fields'] for hit in response.json()['hits']['hit']]

    for result in results:
        for key in result:
            result[key.replace('_', '-')] = result.pop(key)

    return results


def _entry(register, key):
    url = _config(register, 'register')
    response = _get('%s/record/%s.json' % (url, key))
    return response.json()

def _entry_async(register, key, session):
    register = _config(register, 'register')
    url = "%s/record/%s.json" % (register, key)
    current_app.logger.info("ASYNC GET: " + url)
    return session.get(url)

def _unpack_async(async_entry):
    if isinstance(async_entry, Future):
        result = async_entry.result().json()
        current_app.logger.info("ASYNC result: " + json.dumps(result))
        return result
    else:
        return async_entry

def _address_bundle(address):
    address = _entry('address', address)
    address_street = _entry('street', address['street']) if address and 'street' in address else None
    address_street_place = _entry('place', address_street['place']) if address_street and 'place' in address_street else None
    return {
        "address": address,
        "street": address_street,
        "place": address_street_place
    }

def _set_cache(cache_key, value):
    try:
        current_app.cache.set(cache_key, value)
    except Exception as e:
        current_app.logger.warn(e)

def _get_data_from_cache(cache_key):
    data = None
    raw_data = current_app.cache.get(cache_key)
    if raw_data:
        try:
            data = json.loads(raw_data)
        except Exception as e:
            current_app.logger.info("Json could not parse '%s' cache: %s" % (raw_data, e.message))
    return data

@frontend.route('/', methods=['GET', 'POST'])
def index():
    resp = None
    form = SearchForm()
    if form.validate_on_submit():
        establishment_name = form.data.get('establishment_name', '').strip().lower()
        location = form.data.get('location', '').strip().lower()
        try:
            resp = make_response(redirect(url_for('.search', establishment_name=establishment_name, location=location)))
        except Exception as e:
            message = 'There was a problem searching for: %s' % establishment_name
            flash(message)
            abort(500)
    else:
        resp = make_response(render_template('index.html', form=form))

    return resp

@frontend.route('/clear-cache')
def clear_cache():
    message = "Cache cleared: " + str(caching.clear_cache(current_app))
    current_app.logger.info(message)
    return message

@frontend.route('/search')
def search():
    name = request.args.get('establishment_name')
    form = SearchForm(establishment_name=name, location=request.args.get('location'))
    session = FuturesSession(max_workers=12)

    results = _get_data_from_cache('search_results')

    if not results:
        results = _index('food-premises', 'name', name)

        for result in results:
            premises = _entry('premises', result['premises'])
            result['address_bundle'] = {
                'address': _entry_async('address', premises['address'], session)
            }

            ratings = _index('food-premises-rating', 'food-premises', result['food-premises'], 'start-date')
            if ratings:
                result['ratings'] = ratings
                result['rating'] = ratings[0]

        def _resolve_address_level(result, addr_level_key, next_level_key=None):
            for result in results:
                address_part = _unpack_async(result.get('address_bundle').get(addr_level_key))
                result['address_bundle'][addr_level_key] = address_part

                if next_level_key:
                    result['address_bundle'][next_level_key] = _entry_async(next_level_key, address_part[next_level_key], session) if address_part and next_level_key in address_part else None


        _resolve_address_level(result, 'address', 'street')
        _resolve_address_level(result, 'street', 'place')
        _resolve_address_level(result, 'place')

        _set_cache('search_results', json.dumps(results))


    results = sorted(results, key=lambda x: x.get('food-premises'))
    return render_template('results.html', form=form, results=results)

@frontend.route('/rating/<food_premises_rating>')
def rating(food_premises_rating):
    cpfx = 'detail_' + food_premises_rating

    def _as_detail_key(key):
        return "%s_%s" % (cpfx, key)

    def _get_data(cache_key, register, entry_key, use_async=False):
        data = _get_data_from_cache(_as_detail_key(cache_key))
        if not data:
            data = _entry_async(register, entry_key, session) if use_async else _entry(register, entry_key)
        return data

    session = FuturesSession(max_workers=10)

    rating = _get_data('food_premises_rating', 'food-premises-rating', food_premises_rating)
    food_premises = _get_data('food_premises', 'food-premises', rating['food-premises'])
    premises = _get_data('premises', 'premises', food_premises['premises'], use_async=True)

    company_number = food_premises['business']
    company = _get_data('company', 'company', company_number.split(':')[1])
    industry = _get_data('industry', 'industry', company['industry'], use_async=True)

    food_authority = _get_data('food_authority', 'food-authority', food_premises['food-authority'])
    organisation = food_authority['organisation']
    local_authority_eng = _get_data('local_authority_eng', 'local-authority-eng', organisation.split(':')[1], use_async=True)

    ratings = _get_data_from_cache(_as_detail_key('ratings')) or _index('food-premises-rating', 'food-premises', food_premises['food-premises'])
    company_address_bundle = _get_data_from_cache(_as_detail_key('company_address_bundle')) or _address_bundle(company['address'])

    premises = _unpack_async(premises)
    address_bundle = _get_data_from_cache(_as_detail_key('address_bundle')) or _address_bundle(premises['address'])

    industry = _unpack_async(industry)
    local_authority_eng = _unpack_async(local_authority_eng)
    rating = _unpack_async(rating)

    resp = make_response(render_template('rating.html',
        rating=rating,
        ratings=ratings,
        food_premises=food_premises,
        premises=premises,
        address_bundle=address_bundle,
        local_authority_eng=local_authority_eng,
        company=company,
        company_address_bundle=company_address_bundle,
        industry=industry,
        food_authority=food_authority))

    _set_cache(cpfx+'_food_premises_rating', json.dumps(rating))
    _set_cache(cpfx+'_ratings', json.dumps(ratings))
    _set_cache(cpfx+'_food_premises', json.dumps(food_premises))
    _set_cache(cpfx+'_premises', json.dumps(premises))
    _set_cache(cpfx+'_address_bundle', json.dumps(address_bundle))
    _set_cache(cpfx+'_local_authority_eng', json.dumps(local_authority_eng))
    _set_cache(cpfx+'_company', json.dumps(company))
    _set_cache(cpfx+'_company_address_bundle', json.dumps(company_address_bundle))
    _set_cache(cpfx+'_industry', json.dumps(industry))
    _set_cache(cpfx+'_food_authority', json.dumps(food_authority))

    return resp

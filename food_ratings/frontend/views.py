# -*- coding: utf-8 -*-
import requests

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
def _index(index, field, value, sortby = ''):
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

def _address_bundle(address):
    address = _entry('address', address)
    address_street = _entry('street', address['street']) if address and 'street' in address else None
    address_street_place = _entry('place', address_street['place']) if address_street and 'place' in address_street else None
    return {
        "address": address,
        "street": address_street,
        "place": address_street_place
    }

def _load_cookie_from_request(cookie):
    cookie_json = {}
    if cookie in request.cookies:
        cookie_result = request.cookies.get(cookie)
        try:
            cookie_json = json.loads(cookie_result)
        except Exception as e:
            current_app.logger.info("Json could not parse '%s' cookie: %s" % (cookie, e.message))

    return cookie_json


@frontend.route('/',  methods=['GET', 'POST'])
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
    
    for cookie in request.cookies:
        resp.set_cookie(cookie, '', expires=0)

    return resp


@frontend.route('/search')
def search():
    name = request.args.get('establishment_name')
    form = SearchForm(establishment_name=name, location=request.args.get('location'))

    cpfx = 'main_'

    results = []
    cookie_json = {}
    for food_premises_rating_cookie in request.cookies:
        if food_premises_rating_cookie.startswith(cpfx):
            cookie_result = request.cookies.get(food_premises_rating_cookie)
            try:
                cookie_json = json.loads(cookie_result)
                results.append(cookie_json)
            except Exception as e:
                current_app.logger.warn(food_premises_rating_cookie)
                current_app.logger.warn(e)

    set_cookies = False

    if not results:
        set_cookies = True
        results = _index('food-premises', 'name', name)

        for result in results:
            premises = _entry('premises', result['premises'])
            result['address_bundle'] = _address_bundle(premises['address'])

            ratings = _index('food-premises-rating', 'food-premises', result['food-premises'], 'start-date')
            if ratings:
                result['rating'] = ratings[0]

    # results = sorted(results, key=lambda x: x.get('food-premises'))

    resp = make_response(render_template('results.html', form=form, results=results))
    
    if set_cookies:
        for result in results:
            if 'rating' in result:
                resp.set_cookie(cpfx+result.get('rating').get('food-premises-rating'), json.dumps(result))
        
    return resp


@frontend.route('/rating/<food_premises_rating>')
def rating(food_premises_rating):
    cookie_json = _load_cookie_from_request('main_'+food_premises_rating)
    
    cpfx = 'detail_'+food_premises_rating

    rating = _load_cookie_from_request(cpfx+'_rating') or _entry('food-premises-rating', food_premises_rating)
    food_premises = _load_cookie_from_request(cpfx+'_food_premises') or _entry('food-premises', rating['food-premises'])
    premises = _load_cookie_from_request(cpfx+'_premises') or _entry('premises', food_premises['premises'])
    
    address_bundle = _load_cookie_from_request(cpfx+'_address_bundle') or cookie_json.get('address_bundle') or _address_bundle(premises['address'])

    food_authority = _load_cookie_from_request(cpfx+'_food_authority') or _entry('food-authority', food_premises['food-authority'])
    organisation = food_authority['organisation']
    local_authority_eng = _load_cookie_from_request(cpfx+'_local_authority_eng') or _entry('local-authority-eng', organisation.split(':')[1])
    ratings = _load_cookie_from_request(cpfx+'_ratings') or _index('food-premises-rating', 'food-premises', food_premises['food-premises'])

    company_number = food_premises['business']
    company = _load_cookie_from_request(cpfx+'_company') or _entry('company', company_number.split(':')[1])
    industry = _load_cookie_from_request(cpfx+'_industry') or _entry('industry', company['industry'])
    
    company_address_bundle = _load_cookie_from_request(cpfx+'_company_address_bundle') or _address_bundle(company['address'])

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

    resp.set_cookie(cpfx+'_rating', json.dumps(rating))
    resp.set_cookie(cpfx+'_ratings', json.dumps(ratings))
    resp.set_cookie(cpfx+'_food_premises', json.dumps(food_premises))
    resp.set_cookie(cpfx+'_premises', json.dumps(premises))
    resp.set_cookie(cpfx+'_address_bundle', json.dumps(address_bundle))
    resp.set_cookie(cpfx+'_local_authority_eng', json.dumps(local_authority_eng))
    resp.set_cookie(cpfx+'_company', json.dumps(company))
    resp.set_cookie(cpfx+'_company_address_bundle', json.dumps(company_address_bundle))
    resp.set_cookie(cpfx+'_industry', json.dumps(industry))
    resp.set_cookie(cpfx+'_food_authority', json.dumps(food_authority))

    return resp

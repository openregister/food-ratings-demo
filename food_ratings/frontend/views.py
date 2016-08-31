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
    form = SearchForm()
    if form.validate_on_submit():
        establishment_name = form.data.get('establishment_name', '').strip().lower()
        location = form.data.get('location', '').strip().lower()
        try:
            return redirect(url_for('.search', establishment_name=establishment_name, location=location))
        except Exception as e:
            message = 'There was a problem searching for: %s' % establishment_name
            flash(message)
            abort(500)

    resp = make_response(render_template('index.html', form=form))
    for cookie in request.cookies:
        resp.set_cookie(cookie, '', expires=0)

    return resp


@frontend.route('/search')
def search():
    name = request.args.get('establishment_name')
    form = SearchForm(establishment_name=name, location=request.args.get('location'))

    results = _index('food-premises', 'name', name)

    for result in results:
        premises = _entry('premises', result['premises'])
        result['address_bundle'] = _address_bundle(premises['address'])

        ratings = _index('food-premises-rating', 'food-premises', result['food-premises'], 'start-date')
        if ratings:
            result['rating'] = ratings[0]

    resp = make_response(render_template('results.html', form=form, results=results))
    for result in results:
        if 'rating' in result:
            resp.set_cookie(result.get('rating').get('food-premises-rating'), json.dumps(result))
        
    return resp




@frontend.route('/rating/<food_premises_rating>')
def rating(food_premises_rating):
    cookie_json = _load_cookie_from_request(food_premises_rating)
        

    rating = _entry('food-premises-rating', food_premises_rating)
    food_premises = _entry('food-premises', rating['food-premises'])
    premises = _entry('premises', food_premises['premises'])
    
    address_bundle = cookie_json.get('address_bundle') or _address_bundle(premises['address'])

    food_authority = _entry('food-authority', food_premises['food-authority'])
    organisation = food_authority['organisation']
    local_authority_eng = _entry('local-authority-eng', organisation.split(':')[1])
    ratings = _index('food-premises-rating', 'food-premises', food_premises['food-premises'])

    company_number = food_premises['business']
    company = _entry('company', company_number.split(':')[1])
    industry = _entry('industry', company['industry'])
    
    company_address_bundle = _address_bundle(company['address'])

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

    return resp

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
    json
)

from food_ratings.frontend.forms import SearchForm

frontend = Blueprint('frontend', __name__, template_folder='templates')


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
    return render_template('index.html', form=form)


@frontend.route('/search')
def search():
    establishment_name = request.args.get('establishment_name')
    form = SearchForm(establishment_name=establishment_name, location=request.args.get('location'))
    results = [item['fields'] for item in _food_premises_search(establishment_name)]
    for food_premises in results:
        _attach_address(food_premises)
        _attach_local_authority(food_premises)
        _attach_ratings(food_premises)
    current_app.logger.info(results)
    return render_template('results.html', form=form, results=results)


@frontend.route('/premises/<premises>/rating/<food_premises_rating>')
def rating(premises, food_premises_rating):
    premises = _get_food_premises(premises)
    rating = _get_rating(food_premises_rating)
    _attach_address(premises['entry'])
    _attach_local_authority(premises['entry'])
    _attach_ratings(premises['entry'])

    # get lat long from postcode
    postcode_register = current_app.config['POSTCODE_REGISTER']
    url = '%s/postcode/%s.json' % (postcode_register, premises['entry']['postcode'])
    resp = requests.get(url)
    data = resp.json()
    latitude = data['entry']['latitude']
    longitude = data['entry']['longitude']

    #get company address
    company_number = premises['entry']['business']
    company, address = _get_company_details(company_number.split(':')[1])

    current_app.logger.info(company)
    current_app.logger.info(address)

    return render_template('rating.html', rating=rating, food_premises_rating=food_premises_rating, latitude=latitude, longitude=longitude, premises=premises, company=company, address=address)


def _food_premises_search(name):
    search_url = current_app.config['FOOD_PREMISES_SEARCH_URL']
    params = {"q": name, "q.options": "{fields:['name']}"}
    data = requests.get(search_url, params=params)
    return data.json()['hits']['hit']


def _get_food_premises(food_premises):
    rating_register = current_app.config['FOOD_PREMISES_REGISTER']
    url = '%s/food-premises/%s.json' % (rating_register, food_premises)
    resp = requests.get(url)
    return resp.json()


def _get_rating(food_premises):
    rating_register = current_app.config['FOOD_PREMISES_RATING_REGISTER']
    url = '%s/food-premises-rating/%s.json' % (rating_register, food_premises)
    resp = requests.get(url)
    return resp.json()


def _attach_address(food_premises):
    premises_register = current_app.config['PREMISES_REGISTER']
    premises_url = '%s/premises/%s.json' % (premises_register, food_premises['premises'])
    resp = requests.get(premises_url)
    uprn = resp.json()['entry']['address']
    address_register = current_app.config['ADDRESS_REGISTER']
    address_url = '%s/address/%s.json' % (address_register, uprn)
    resp = requests.get(address_url).json()
    food_premises['property'] = resp['entry'].get('property')
    food_premises['street'] = resp['entry'].get('street')
    food_premises['town'] = resp['entry'].get('town')
    food_premises['postcode'] = resp['entry'].get('postcode')


def _attach_local_authority(food_premises):
    if food_premises.get('local-authority'):
        local_authority_register = current_app.config['LOCAL_AUTHORITY_REGISTER']
        la_url = '%s/local-authority/%s.json' % (local_authority_register, food_premises['local-authority'])
        data = requests.get(la_url).json()
        food_premises['local-authority-name'] = data['entry']['name']
        food_premises['local-authority-website'] = data['entry']['website']


def _attach_ratings(food_premises):
    search_url = current_app.config['FOOD_PREMISES_RATING_SEARCH_URL']
    premises_key = food_premises.get('food_premises')
    if not premises_key:
        premises_key = food_premises.get('food-premises')
    params = {"q": premises_key, "q.options": "{fields:['food_premises']}"}
    data = requests.get(search_url, params=params)
    ratings = [rating['fields'] for rating in data.json()['hits']['hit']]
    food_premises['ratings'] = ratings
    #TODO proper sort by start date
    if len(ratings) > 0:
        food_premises['last_inspection'] = ratings[0]
        food_premises['inspection_history'] = ratings[1:]
    else:
        food_premises['last_inspection'] = {}


def _get_company_details(company_number):
    co_house_api_key = current_app.config['COMPANIES_HOUSE_API_KEY']
    headers = {'Authorization': 'Basic '+co_house_api_key}
    try:
        url = 'https://api.companieshouse.gov.uk/company/%s' % company_number
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        current_app.logger.info(res.json())
        company = res.json()
        url = 'https://api.companieshouse.gov.uk/company/%s/registered-office-address' % company_number
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        address = res.json()
        return (company, address)
    except Exception as e:
        current_app.logger.info(e)
        return (canned_company_data, {})


canned_company_data = {"can_file": True, "has_insolvency_history": False, "jurisdiction": "england-wales", "sic_codes": ["56101"], "etag": "ae17d388cfeae6306b800bceebb044a3e97ffcfe", "registered_office_address": {"country": "United Kingdom", "locality": "London", "postal_code": "W1T 3LJ", "address_line_1": "1st Floor 14-15 Berners Street"}, "undeliverable_registered_office_address": False, "annual_return": {"next_due": "2016-05-18", "last_made_up_to": "2015-04-20", "next_made_up_to": "2016-04-20", "overdue": False}, "company_number": "07228130", "last_full_members_list_date": "2015-04-20", "date_of_creation": "2010-04-20", "has_been_liquidated": False, "accounts": {"next_due": "2016-03-31", "last_accounts": {"type": "full", "made_up_to": "2014-06-29"}, "accounting_reference_date": {"day": "30", "month": "06"}, "next_made_up_to": "2015-06-30", "overdue": False}, "company_name": "BYRON HAMBURGERS LIMITED", "company_status": "active", "has_charges": True, "type": "ltd"}


# dummy API
# old stub api data
# @frontend.route('/industry.openregister.org/industry/<code>')
# def industry_register(code):
#     return jsonify({
#         'industry':'56101',
#         'name':'Licensed restaurants'
#     })


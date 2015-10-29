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

import requests

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
    # find the item
    form = SearchForm(business=request.args.get('establishment_name'), location=request.args.get('location'))
    premises = _food_premises_search()
    # get addresses
    for p in premises:
        _attach_address(p)


    return render_template('results.html', form=form, results=premises)


# dummy API
@frontend.route('/industry.openregister.org/industry/<code>')
def industry_register(code):
    return jsonify({
        'industry':'56101',
        'name':'Licensed restaurants'
    })

@frontend.route('/local-authority.openregister.org/local-authority/<code>')
def local_authority_register(code):
    return jsonify({
        'local-authority':'00AG',
        'name':'Camden',
        'website':'https://www.camden.gov.uk'
    })

@frontend.route('/company.openregister.org/company/<company>')
def company_register(company):
    return jsonify({
        'company':'07228130',
        'name': 'BYRON HAMBURGERS LIMITED',
        'address':'5155313',
        'industry':'56101',
        'start-date':'2010-04-20'
    })

@frontend.route('/food-premises.openregister.org/food-premises/<food_premises>')
def food_premises_register(food_premises):
    return jsonify({
        'food-premises':'759332',
        'name':'Byron',
        'business':'company:07228130',
        'premises':'15662079000',
        'local-authority':'00AG',
        'food-premises-types':['Restaurant','Cafe','Canteen']
    })


@frontend.route('/food-premises.openregister.org/some-search-url')
def food_premises_register_search():
    name = request.args.get('establishment_name')
    return jsonify({'results': [
        {'food-premises':'759332',
        'name':'Byron',
        'business':'company:07228130',
        'premises':'15662079000',
        'local-authority':'00AG',
        'food-premises-types':['Restaurant','Cafe','Canteen']},

        {'food-premises':'785709',
        'name':'Byron',
        'business':'company:07228130',
        'premises':'15610045000',
        'local-authority':'00AG',
        'food-premises-types':['Restaurant','Cafe','Canteen']},

        {'food-premises':'516226',
        'name':'Byron',
        'business':'company:07228130',
        'premises':'14445100000',
        'local-authority':'00AG',
        'food-premises-types':['Restaurant','Cafe','Canteen']}
        ]
    })


@frontend.route('/food-premises-rating.openregister.org/food-premises-rating/759332-2014-04-09')
def food_premises_rating_register_1(food_premises_rating):
    return jsonify({
        "food-premises-rating":"759332-2014-04-09",
        "food-premises":"759332",
        "food-premises-rating-value":"4",
        "food-premises-rating-hygiene-score":"5",
        "food-premises-rating-structural-score":"10",
        "food-premises-rating-confidence-in-management-score":"5",
        "inspector":"local-authority:00AG",
        "food-premises-rating-reply":"",
        "start-date":"2014-04-09"
    })

@frontend.route('/food-premises-rating.openregister.org/food-premises-rating/759332-2015-08-27')
def food_premises_rating_register_2(food_premises_rating):
    return jsonify({
        "food-premises-rating":"759332-2015-08-27",
        "food-premises":"759332",
        "food-premises-rating-value":"1",
        "food-premises-rating-hygiene-score":"15",
        "food-premises-rating-structural-score":"15",
        "food-premises-rating-confidence-in-management-score":"20",
        "inspector":"local-authority:00AG",
        "food-premises-rating-reply":"I agree with the inspection results but have since carried out the following improvements:\n\nThere is a new manager and/or new staff. The staff have been trained/retrained/given instruction/are under revised supervisory arrangements.\n\nThe points raised by the Environmental Health Officers were acted upon immediately and we look forward to welcoming them back for a re-inspection when we will be delighted to demonstrate our high standards at this restaurant.\n\nThe conditions found at the time of the inspection were not typical of the normal conditions maintained at the establishment and arose because: Historically, cooking temperature records were available. However, on the day of the inspection this was not the case.",
        "start-date":"2015-08-27"
    })

@frontend.route('/rating/<fhrs_id>')
def rating(fhrs_id):
    rating = {'name': 'Byron Hamburgers', 'premises': '1a St Giles High Street, WC2H 8AG', 'inspection_date': '27 August 2015'}

    # get lat long from postcode
    postcode_register = current_app.config['POSTCODE_REGISTER']
    url = '%s/postcode/%s' % (postcode_register, 'WC2H%208AG.json')
    resp = requests.get(url)
    data = resp.json()
    latitude = data['entry']['latitude']
    longitude = data['entry']['longitude']
    return render_template('rating.html', rating=rating, fhrs_id=fhrs_id, latitude=latitude, longitude=longitude, premises=15662079000, company='07228130')


def _food_premises_search():
    resp = food_premises_register_search()
    results = json.loads(resp.data)
    current_app.logger.info(json.loads(resp.data))
    return results['results']

def _attach_address(food_premises):
    premises_register = current_app.config['PREMISES_REGISTER']
    premises_url = '%s/premises/%s.json' % (premises_register, food_premises['premises'])
    resp = requests.get(premises_url)
    uprn = resp.json()['entry']['address']
    current_app.logger.info(resp.json()['entry']['address'])

    address_register = current_app.config['ADDRESS_REGISTER']
    address_url = '%s/address/%s.json' % (address_register, uprn)
    resp = requests.get(address_url).json()
    food_premises['property'] = resp['entry'].get('property')
    food_premises['street'] = resp['entry'].get('street')
    food_premises['town'] = resp['entry'].get('town')
    food_premises['postcode'] = resp['entry'].get('postcode')

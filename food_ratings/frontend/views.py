from flask import (
    render_template,
    Blueprint,
    flash,
    abort,
    current_app,
    request,
    redirect,
    url_for,
    jsonify
)

import requests

from food_ratings.frontend.forms import SearchForm

frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/',  methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        business = form.data.get('business', '').strip().lower()
        location = form.data.get('location', '').strip().lower()
        try:
            return redirect(url_for('.search', business=business, location=location))
        except Exception as e:
            message = 'There was a problem searching for: %s' % business
            flash(message)
            abort(500)
    return render_template('index.html', form=form)


@frontend.route('/search')
def search():
    # find the item
    form = SearchForm(business=request.args['business'], location=request.args['location'])
    results = [{'name': 'Byron Hamburgers', 'premises': '1a St Giles High Street, WC2H 8AG', 'inspection_date': '27 August 2015', 'rating': '1 – Major improvement needed'}, {'name': 'Byron Hamburgers', 'premises': '6 Rathbone Place, London, W1T 1HL', 'inspection_date': '1 December 2014', 'rating': '4 – Good'}, {'name': 'Byron Hamburgers', 'premises': '6 Store Street, London, WC1E 7DQ', 'inspection_date': '22 July 2012', 'rating': '5 – Very good'}]
    return render_template('results.html', form=form, results=results)


@frontend.route('/company.openregister.org/company/<company>')
def company_register(company):
    return jsonify({'company':'07228130','name': 'BYRON HAMBURGERS LIMITED','address':'10033530330','industry':'56101','start-date':'2010-04-20'})


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
    return render_template('rating.html', rating=rating, fhrs_id=fhrs_id, latitude=latitude, longitude=longitude)

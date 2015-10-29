from flask_wtf import Form
from wtforms import StringField

class SearchForm(Form):
    establishment_name = StringField()
    location = StringField()

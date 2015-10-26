
from flask import (
    render_template,
    Blueprint
)

frontend = Blueprint('frontend', __name__, template_folder='templates')

@frontend.route("/")
def index():
    return render_template('index.html')


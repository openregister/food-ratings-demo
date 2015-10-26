import os
from food_ratings.factory import create_app
app = create_app(os.environ['SETTINGS'])

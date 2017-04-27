# -*- coding: utf-8 -*-
import os

class Config(object):
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_ROOT, os.pardir))
    SECRET_KEY = os.environ.get('SECRET_KEY')
    REDIS_URL = os.environ.get('REDISCLOUD_URL')
    PREMISES_REGISTER = os.environ.get('PREMISES_REGISTER')
    COMPANY_REGISTER = os.environ.get('COMPANY_REGISTER')
    ADDRESS_REGISTER = os.environ.get('ADDRESS_REGISTER')
    STREET_REGISTER = os.environ.get('STREET_REGISTER')
    PLACE_REGISTER = os.environ.get('PLACE_REGISTER')
    INDUSTRIAL_CLASSIFICATION_REGISTER = os.environ.get('INDUSTRIAL_CLASSIFICATION_REGISTER')
    FOOD_PREMISES_REGISTER = os.environ.get('FOOD_PREMISES_REGISTER')
    FOOD_PREMISES_RATING_REGISTER = os.environ.get('FOOD_PREMISES_RATING_REGISTER')
    LOCAL_AUTHORITY_ENG_REGISTER = os.environ.get('LOCAL_AUTHORITY_ENG_REGISTER')
    FOOD_AUTHORITY_REGISTER = os.environ.get('FOOD_AUTHORITY_REGISTER')
    COMPANIES_HOUSE_API_KEY = os.environ.get('COMPANIES_HOUSE_API_KEY')


class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'local-dev-not-secret')


class TestConfig(Config):
    TESTING = True

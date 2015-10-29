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
    POSTCODE_REGISTER = os.environ.get('POSTCODE_REGISTER')
    FOOD_PREMISES_REGISTER = os.environ.get('FOOD_PREMISES_REGISTER')



class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'local-dev-not-secret')

class TestConfig(Config):
    TESTING = True

import os

SECRET_KEY = os.environ.get('SECRET_KEY',
                                '51f52814-0071-11e6-a247-000ec6c2372c')
DEBUG = True
MONGODB_HOST = 'mongodb'
MONGODB_DB = 'scsrAPI'

# flask app
RANDOM_STRING = '1324'
JWT_SECRET_KEY = '5q4w3e2r1'

APP_NAME = "My blog"
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000
DEBUG = True

# database
POSTGRES = {
    'user': 'postgres',
    'pw': '123',
    'db': 'postgres',
    'host': '127.0.0.1',
    'port': '5432',
}

DB_URL = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' %POSTGRES


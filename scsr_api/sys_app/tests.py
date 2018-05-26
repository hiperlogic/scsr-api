import json
import unittest
from datetime import datetime, timedelta
from mongoengine.connection import _get_db
from application import ScsrAPP


from sys_app.models.base_auth import App, Access
from settings import MONGODB_HOST

class AppTest(unittest.TestCase):
    
    def setUp(self):
        self.db_name = 'scsr-api-test2'
        
        self.app_factory = ScsrAPP(
            MONGODB_SETTINGS = {'DB': self.db_name,
                'HOST': MONGODB_HOST},
            TESTING = True,
            WTF_CSRF_ENABLED = False,
            SECRET_KEY = 'mySecret!').APP
        self.app = self.app_factory.test_client()

    def tearDown(self):
        db = _get_db()
        db.client.drop_database(db)

    def app_dict(self):
        return json.dumps(dict(
            app_id = "Scsr_Client",
            app_secret = "scsr_secret"
        ))

    def test_create_app(self):
        #basic registration
        rv = self.app.post('/apps/',
            data = self.app_dict(),
            content_type = 'application/json')
        assert rv.status_code == 200

        #missing app_secret
        dado=json.dumps(dict(
            app_id = "Scsr_Client"))
        rv = self.app.post('/apps/',
            data = dado,
            content_type = 'application/json')
        assert "MISSING_APP_ID_OR_APP_SECRET" in str(rv.data)

        #repeat registration
        rv = self.app.post('/apps/',
            data = self.app_dict(),
            content_type = 'application/json')
        assert "APP_ID_ALREADY_EXISTS" in str(rv.data)


    def test_token_generation(self):
        dado=json.dumps(dict(
            app_id = "Scsr_Client"))

        rv = self.app.post('/apps/',
            data = self.app_dict(),
            content_type = 'application/json')
        assert rv.status_code == 200

        #generate access token
        rv = self.app.post('/apps/access_token/',
            data = self.app_dict(),
            content_type = 'application/json')
        token = json.loads(rv.data.decode('utf-8')).get('token')
        assert token is not None

        rv=self.app.post('/apps/access_token/',
            data = dado,
            content_type = 'application/json')
        assert "MISSING_APP_ID_OR_APP_SECRET" in str(rv.data)

        #incorrect app_secret
        dado2=json.dumps(dict(
            app_id = "Scsr_Client",
            app_secret = "secreto errado"))
        rv=self.app.post('/apps/access_token/',
            data = dado2,
            content_type = 'application/json')
        assert "INCORRECT_CREDENTIALS" in str(rv.data)

        #Test working token
        rv = self.app.get('/games/',
            headers={'X-APP-ID': 'Scsr_Client', 'X-APP-TOKEN': token},
            content_type = 'application/json')
        assert rv.status_code == 200

        #test bad_token
        rv = self.app.get('/games/',
            headers={
                'X-APP-ID': 'Scsr_Client',
                'X-APP-TOKEN': token+"lll"
            },
            content_type = 'application/json')
        assert rv.status_code == 403

        #test expired token
        now = datetime.utcnow().replace(second=0, microsecond = 0)
        expires = now + timedelta(days=-31)
        access = Access.objects.first() # pylint: disable=no-member
        access.expires = expires
        access.save()
        rv = self.app.get('/games/',
            headers={
                'X-APP-ID': 'Scsr_Client',
                'X-APP-TOKEN': token
            },
            content_type = 'application/json')
        assert "TOKEN_EXPIRED" in str(rv.data)

        

        
        

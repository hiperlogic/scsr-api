import json
import unittest
from datetime import datetime, timedelta
from mongoengine.connection import _get_db
from application import ScsrAPP


#import the authorization mechanism


from settings import MONGODB_HOST

class ScsrTest(unittest.TestCase):
    
    def setUp(self):
        print("#"*130)
        print(" "*40+"Testing SCSR View (Endpoints)")
        print("#"*130)
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

    #Test to add_games in the system.
        # The add_games endpoint is an administrative endpoint, so, it needs an administrative ID in order to fulfill its tasks
    def test_add_games(self):
        pass
        
        
class ModelTest(unittest.TestCase):
    
    the_test="Models View (Endpoints)"

    def setUp(self):
        print("#"*130)
        print(" "*40+"Testing "+self.the_test)
        print("#"*130)
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

    #Test to add_games in the system.
        # The add_games endpoint is an administrative endpoint, so, it needs an administrative ID in order to fulfill its tasks
    def test_elements(self):
        self.tearDown()
        self.the_test="Element Models"
        self.setUp()
        from scsr.models.test_elements import ElementModelTest

    def test_behaviors(self):
        self.tearDown()
        self.the_test="Behavior Models"
        self.setUp()
        from scsr.models.test_behaviors import BehaviorModelTest

    def test_persuasive_function(self):
        self.tearDown()
        self.the_test="Persuasive Functions"
        self.setUp()
        from scsr.models.test_persuasive_function import PersuasiveFunctionModelTest

    def test_aesthetic_function(self):
        self.tearDown()
        self.the_test="Aesthetic Functions"
        self.setUp()
        from scsr.models.test_aesthetic_function import AestheticFunctionModelTest

    def test_orchestration_function(self):
        self.tearDown()
        self.the_test="Orchestration Functions"
        self.setUp()
        from scsr.models.test_orchestration_function import OrchestrationFunctionModelTest

    def test_reification_function(self):
        self.tearDown()
        self.the_test="Reification Functions"
        self.setUp()
        from scsr.models.test_reification_function import ReificationFunctionModelTest


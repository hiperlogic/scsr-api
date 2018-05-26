import json
import unittest
from datetime import datetime, timedelta
from mongoengine.connection import _get_db
from application import ScsrAPP


#import the authorization mechanism
from sys_app.models.base_auth import App, Access


from game.models.game import GameDB, GameAO
from game.models.genre import GenreDB, GenreAO
from game.models.user_game_genre import UserGameGenreDB, GameGenreQuantificationDB, GamesGenresDB, GamesGenresAO
from settings import MONGODB_HOST

class ScsrModelTest(unittest.TestCase):
    
    def setUpClass(cls):
        print("#"*130)
        print(" "*40+"Testing SCSR Model")
        print("#"*130)
        self.db_name = 'scsr-api-test2'
        
        self.app_factory = ScsrAPP(
            MONGODB_SETTINGS = {'DB': self.db_name,
                'HOST': MONGODB_HOST},
            TESTING = True,
            WTF_CSRF_ENABLED = False,
            SECRET_KEY = 'mySecret!').APP
        self.app = self.app_factory.test_client()

    def tearDownClass(cls):
        db = _get_db()
        db.client.drop_database(db)

    #Test to add_games in the system.
        # The add_games endpoint is an administrative endpoint, so, it needs an administrative ID in order to fulfill its tasks
    def test_add_games(self):
        pass
        
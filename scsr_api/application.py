from flask import Flask, jsonify
from flask_mongoengine import MongoEngine
from sys_app.AuthError import AuthError
from flask_cors import CORS
from mongoengine.connection import _get_db


db = MongoEngine()
the_log=None

class ScsrAPP:
    
    
    def __init__(self, *args, **kwargs):
        self.APP  = Flask(__name__)
        @self.APP.errorhandler(AuthError)
        def handle_auth_error(ex):
            print("Error Called")
            response = jsonify(ex.error)
            response.status_code = ex.status_code
            return response
        # Load config
        self.APP.config.from_pyfile('settings.py')


        # apply overrides for tests
        
        
        self.APP.config.update(kwargs)
        
        # setup db
        db.init_app(self.APP)

        #setup logger
        the_log = self.APP.logger
        
        
        # import blueprints
        from home.views import home_app
        from scsr.views import ScsrView
        from startupBattle.views import StartupBattleView
        from user.views import user_app
        from sys_app.views import app_app

        scsrView=ScsrView()
        scsrView.registerBlueprints(self.APP)

        startupBattle = StartupBattleView(self.APP)

        # register blueprints
        self.APP.register_blueprint(home_app)
        #self.APP.register_blueprint(scsr_app)
        self.APP.register_blueprint(app_app)
        #self.APP.register_blueprint(battles_app)
        self.APP.register_blueprint(user_app)
        CORS(self.APP)

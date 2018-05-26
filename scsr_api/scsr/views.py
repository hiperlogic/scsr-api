from flask import Blueprint

from scsr.api import ScsrAPI

class ScsrView:
    scsr_app = None
    def __init__(self):
        self.scsr_app = Blueprint('scsr_app', __name__)

        self.games_view = ScsrAPI.as_view('games')

        self.scsr_app.add_url_rule('/games/', defaults={'game_id':None},
            view_func = self.games_view, methods=['GET',])
        self.scsr_app.add_url_rule('/games/', view_func=self.games_view, methods=['POST',])
        self.scsr_app.add_url_rule('/games/<int:game_id>', view_func=self.games_view,
            methods=['GET', 'PUT', 'DELETE',])

    def registerBlueprints(self,APP):
        APP.register_blueprint(self.scsr_app)
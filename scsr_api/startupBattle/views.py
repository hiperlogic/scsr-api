from flask import Blueprint

from startupBattle.api import PublicBattles, PrivateBattles

class StartupBattleView:
    battles_app = None

    def __init__(self, APP=None):

        self.battles_app = Blueprint('battles_app', __name__)

        self.games_view = PublicBattles.as_view('publicBattles')
        self.private_games_view = PrivateBattles.as_view('privateBattles')

        self.battles_app.add_url_rule('/api/battles/public', defaults={'battle_id':None},
            view_func = self.games_view, methods=['GET',])
        self.battles_app.add_url_rule('/api/battles/public/<int:game_id>', view_func=self.games_view, methods=['GET',])

        self.battles_app.add_url_rule('/api/battles/private', defaults={'battle_id':None},
            view_func = self.private_games_view, methods=['GET',])
        self.battles_app.add_url_rule('/api/battles/private/<int:game_id>', view_func=self.private_games_view, methods=['GET',])
        if(APP):
            self.registerBlueprint(APP)

    def registerBlueprint(self,APP):
        APP.register_blueprint(self.battles_app)
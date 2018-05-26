from flask.views import MethodView
from flask import jsonify, request, abort
from flask_cors import cross_origin
from sys_app.decorators import requires_auth, app_required

class ScsrAPI(MethodView):
    
    

    games = [
        {"id":1, "game": u"Don't Starve", "studio": u"Klei", "links":[{"rel": "self", "href": "/games/1"}]},
        {"id":2, "game": u"Dengue Wars", "studio": u"AEEE", "links":[{"rel": "self", "href": "/games/2"}]},
        {"id":3, "game": u"Clash Royale", "studio": u"Supercell", "links":[{"rel": "self", "href": "/games/3"}]},
    ]

    @app_required
    def get(self, game_id):
        if(game_id):
            return jsonify({"game": self.games[game_id - 1]})
        else:
            return jsonify({"games": self.games})

    @requires_auth
    def post(self):
        if not request.json or (not 'game' in request.json) or (not 'studio' in request.json):
            abort(400)
        game = {
            "id": len(self.games) +1,
            "game": request.json["game"],
            "studio": request.json["studio"],
            "links":[{"rel": "self", "href": "/games/" + str(len(self.games) +1) }]
        }
        self.games.append(game)
        return jsonify({'game': game}), 201

    @requires_auth
    def put(self, game_id):
        if not request.json or (not 'game' in request.json) or (not 'studio' in request.json) or (not game_id):
            abort(400)
        game=self.games[game_id - 1]
        game["game"] = request.json["game"]
        game["studio"] = request.json["studio"]
        return jsonify({"game":game}), 200

    @requires_auth
    def delete(self,game_id):
        del self.games[game_id - 1]
        return jsonify({}), 204

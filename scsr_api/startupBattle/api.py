from flask.views import MethodView
from flask import jsonify, request, abort
from flask_cors import cross_origin
from sys_app.decorators import requires_auth

class PublicBattles(MethodView):
    
    publicBattles = [
        {
            "id": 1111,
            "name": 'Startup NYC',
            "sponsor": 'Alec Pesola',
            "seedFund": '500k'
        },
        {
            "id": 1112,
            "name": 'Startup Ontario',
            "sponsor": 'Ryan Chenkie',
            "seedFund": '750k'
        },
        {
            "id": 1113,
            "name": 'Startup Uttah',
            "sponsor": 'Diego Poza',
            "seedFund": '550k'
        },
        {
            "id": 1114,
            "name": 'Startup Australia',
            "sponsor": 'Eugene Kogan',
            "seedFund": '500k'
        },
        {
            "id": 1115,
            "name": 'Startup Buenos Aires',
            "sponsor": 'Sebastian Peyrott',
            "seedFund": '600k'
        },
        {
            "id": 1116,
            "name": 'Startup Lagos',
            "sponsor": 'Prosper Otemuyiwa',
            "seedFund": '650k'
        },
        {
            "id": 1117,
            "name": 'Startup Oslo',
            "sponsor": 'Mark Fish',
            "seedFund": '600k'
        },
        {
            "id": 1118,
            "name": 'Startup Calabar',
            "sponsor": 'Christian Nwamba',
            "seedFund": '800k'
        },
        {
            "id": 1119,
            "name": 'Startup Nairobi',
            "sponsor": 'Aniedi Ubong',
            "seedFund": '700k'
        }
    ]
    
    @cross_origin(headers=["Content-Type", "Authorization"])
    def get(self, battle_id):
        if(battle_id):
            for battle in self.publicBattles:
                if battle["id"]==battle_id:
                    return jsonify(battle)
            return jsonify({}),200
        else:
            return jsonify(self.publicBattles)
    

class PrivateBattles(MethodView):
    privateBattles = [
        {
            "id": 2111,
            "name": 'Startup Seattle',
            "sponsor": 'Mark Zuckerberg',
            "seedFund": '10M'
        },
        {
            "id": 2112,
            "name": 'Startup Vegas',
            "sponsor": 'Bill Gates',
            "seedFund": '20M'
        },
        {
            "id": 2113,
            "name": 'Startup Addis-Ababa',
            "sponsor": 'Aliko Dangote',
            "seedFund": '8M'
        },
        {
            "id": 2114,
            "name": 'Startup Abuja',
            "sponsor": 'Femi Otedola',
            "seedFund": '5M'
        },
        {
            "id": 2115,
            "name": 'Startup Paris',
            "sponsor": 'Jeff Bezos',
            "seedFund": '1.6M'
        },
        {
            "id": 2116,
            "name": 'Startup London',
            "sponsor": 'Dave McClure',
            "seedFund": '1M'
        },
        {
            "id": 2117,
            "name": 'Startup Oslo',
            "sponsor": 'Paul Graham',
            "seedFund": '2M'
        },
        {
            "id": 2118,
            "name": 'Startup Bangkok',
            "sponsor": 'Jeff Clavier',
            "seedFund": '5M'
        },
        {
            "id": 2119,
            "name": 'Startup Seoul',
            "sponsor": 'Paul Buchheit',
            "seedFund": '4M'
        }
    ]
    
    @cross_origin(headers=["Content-Type", "Authorization"])
    @cross_origin(headers=["Access-Control-Allow-Origin", "*"])
    @requires_auth
    def get(self, battle_id):
        if(battle_id):
            for battle in self.privateBattles:
                if battle["id"]==battle_id:
                    return jsonify(battle)
            return jsonify({}),200
        else:
            return jsonify(self.privateBattles)

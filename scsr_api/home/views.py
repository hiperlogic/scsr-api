# coding: utf-8
from flask import Blueprint

home_app = Blueprint('home_app', __name__)

@home_app.route('/')
def home():
    return "Olá Flask! Funciona... Rearruma automático?"

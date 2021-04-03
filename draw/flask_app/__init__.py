from flask import Blueprint

app = Blueprint("app", __name__)

from . import events, routes

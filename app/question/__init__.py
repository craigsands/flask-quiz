from flask import Blueprint

bp = Blueprint('question', __name__)

from app.question import routes

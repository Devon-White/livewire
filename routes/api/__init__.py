from flask import Blueprint

api_bp = Blueprint('api', __name__)

from .get_embed_token import *
from .main_swml import *
from .call_info import *
from .call_status import *
from .create_sat import *
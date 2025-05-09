from flask import Blueprint

api_bp = Blueprint('api', __name__)

from .main_swml import *
from .call_info import *
from .call_status import *
from .create_sat import *
from .widget_config import *
from .swml_handler import *
from .create_member import *
from .subscriber_offline import *


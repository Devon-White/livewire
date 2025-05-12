from flask import Blueprint

api_bp = Blueprint("api", __name__)

from .call_info import *
from .call_status import *
from .create_member import *
from .create_sat import *
from .main_swml import *
from .subscriber_offline import *
from .swml_handler import *
from .widget_config import *

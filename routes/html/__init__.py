from flask import Blueprint
import logging

logger = logging.getLogger(__name__)

html_bp = Blueprint('html', __name__)

from .index import *
from .subscriber import *
from .login import *
from .signup import *
from .logout import *
from .call import * 
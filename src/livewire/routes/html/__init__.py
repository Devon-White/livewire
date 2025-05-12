import logging

from flask import Blueprint

logger = logging.getLogger(__name__)

html_bp = Blueprint("html", __name__)

from .call import *
from .index import *
from .login import *
from .logout import *
from .signup import *
from .subscriber import *

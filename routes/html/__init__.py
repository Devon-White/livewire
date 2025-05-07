from flask import Blueprint

html_bp = Blueprint('html', __name__)

from .index import *
from .subscriber import *
from .login import *
from .signup import *
from .logout import * 
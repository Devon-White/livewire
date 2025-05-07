from signalwire_swaig import SWAIG
from routes.html import html_bp
from routes.api import api_bp
from routes.swaig_functions import auto_register_swaig_endpoints

swaig = SWAIG()  # No app yet!


def register_app_blueprints(app):
    app.register_blueprint(html_bp)
    app.register_blueprint(api_bp)
    
    # We need to register the SWAIG endpoints since we are using Flask Blueprints
    auto_register_swaig_endpoints()
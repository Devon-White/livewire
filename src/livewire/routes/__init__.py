from signalwire_swaig import SWAIG

from livewire.routes.api import api_bp
from livewire.routes.html import html_bp
from livewire.routes.swaig_functions import auto_register_swaig_endpoints

swaig = SWAIG()  # No app yet!


def register_app_blueprints(app) -> None:
    """
    Register all Flask Blueprints with the application and auto-register SWAIG endpoints.

    Args:
        app (Flask): The Flask application instance.
    """
    app.register_blueprint(html_bp)
    app.register_blueprint(api_bp)

    # We need to register the SWAIG endpoints since we are using Flask Blueprints
    auto_register_swaig_endpoints()

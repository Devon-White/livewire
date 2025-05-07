from flask import Flask
from ngrok import ngrok
from setup import update_swml_script
from dotenv import load_dotenv
import os
from routes import swaig, register_app_blueprints
import logging
import base64
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)  # Generate a new secret key on each start

    # Initialize SWAIG
    swaig.init_app(app)
    # Register blueprints
    register_app_blueprints(app)


    return app

def setup_app_config(app, **kwargs):
    app.config['PUBLIC_URL'] = kwargs.get('public_url')
    app.config['C2C_TOKEN'] = os.getenv('C2C_TOKEN')
    app.config['SIGNALWIRE_AUTH'] = (
        "Basic " +
        base64.b64encode(
            f"{os.getenv('SIGNALWIRE_PROJECT')}:{os.getenv('SIGNALWIRE_TOKEN')}".encode()
        ).decode()
    )

if __name__ == '__main__':
    load_dotenv()
    app = create_app()
    port = 5000
    listener = ngrok.forward(f"localhost:{port}", authtoken_from_env=True)
    public_url = listener.url()
    logger.info(f"ngrok tunnel running at: {public_url}")
    setup_app_config(app, public_url=public_url)
    update_swml_script(public_url, app.config['SIGNALWIRE_AUTH'])
    app.run(debug=False, port=port)
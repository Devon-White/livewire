from flask import Flask
from ngrok import ngrok
from setup import update_swml_script
from dotenv import load_dotenv
import os

from routes.main import main_bp, set_public_url
from routes import swaig

def create_app():
    load_dotenv()
    app = Flask(__name__)

    # Initialize SWAIG and set the proxy
    swaig.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)

    # Import route modules to register SWAIG endpoints. Needs to be done after the app is created.
    import routes.verify_customer as _
    import routes.send_user_info as _ 

    return app

if __name__ == '__main__':
    app = create_app()
    port = 5000
    listener = ngrok.forward(f"localhost:{port}", authtoken_from_env=True)
    public_url = listener.url()
    print(f"ngrok tunnel running at: {public_url}")
    set_public_url(public_url)
    update_swml_script(public_url)
    app.run(debug=False, port=port)
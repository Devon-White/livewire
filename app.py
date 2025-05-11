from flask import Flask, request, redirect, url_for, flash
from ngrok import ngrok
from dotenv import load_dotenv
import os
import secrets
from routes import swaig, register_app_blueprints
import logging
from utils.session_utils import has_sw_credentials, is_subscriber_logged_in

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Get session secret from environment or generate if not set
    session_secret = secrets.token_hex(16)
    
    app.secret_key = session_secret
    
    # Configure sessions
    app.config['SESSION_PERMANENT'] = False  # Non-permanent sessions
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] =  3600  # Default 1 hour
    
    # Initialize SWAIG
    swaig.init_app(app)
    # Register blueprints
    register_app_blueprints(app)
    
    # Global middleware for authentication
    @app.before_request
    def auth_middleware():
        # Only protect HTML routes (except index)
        if (request.endpoint and 
            request.endpoint.startswith('html.') and 
            request.endpoint != 'html.index'):
            
            # Log the protected route
            logger.info(f"Protected route: {request.endpoint}")
            
            # Check for SignalWire credentials using the utility function
            if not has_sw_credentials():
                logger.warning(f"Authentication failed for {request.path}")
                flash("Please provide your SignalWire credentials first.")
                return redirect(url_for('html.index'))
                
            # Additional check for subscriber page
            if request.endpoint == 'html.subscriber_page':
                # Use the utility function to check subscriber login
                if not is_subscriber_logged_in():
                    logger.warning(f"Subscriber login required for {request.path}")
                    flash("Please log in as a subscriber first.")
                    return redirect(url_for('html.login'))

    return app

def setup_app_config(app, **kwargs):
    app.config['PUBLIC_URL'] = kwargs.get('public_url')

if __name__ == '__main__':
    load_dotenv()
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    listener = ngrok.forward(f"localhost:{port}", authtoken_from_env=True)
    public_url = listener.url()
    logger.info(f"ngrok tunnel running at: {public_url}")
    setup_app_config(app, public_url=public_url)
    # Set debug based on environment variable
    app.debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(port=port, host='0.0.0.0')
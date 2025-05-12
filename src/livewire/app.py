import logging
import os
import secrets
import sys

from dotenv import load_dotenv
from flask import Flask, flash, redirect, request, url_for
from ngrok import ngrok

from livewire.routes import register_app_blueprints, swaig
from livewire.utils.session_utils import (has_sw_credentials,
                                          is_subscriber_logged_in)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Constants
SESSION_LIFETIME_SECONDS: int = int(os.environ.get("FLASK_SESSION_LIFETIME", 3600))
DEFAULT_PORT: int = int(os.environ.get("PORT", 8080))
REPLIT_ENV: bool = "REPL_ID" in os.environ


def create_app() -> Flask:
    """
    Create and configure the Flask application for the LiveWire demo.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(
        __name__, template_folder="../../templates", static_folder="../../static"
    )

    # Get session secret from environment or generate if not set
    session_secret = os.environ.get("FLASK_SESSION_SECRET", secrets.token_hex(16))
    app.secret_key = session_secret

    # Configure sessions
    app.config["SESSION_PERMANENT"] = False  # Non-permanent sessions
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = SESSION_LIFETIME_SECONDS

    # Initialize SWAIG
    swaig.init_app(app)
    # Register blueprints
    register_app_blueprints(app)

    # Global middleware for authentication
    @app.before_request
    def auth_middleware() -> None:
        """
        Middleware to enforce authentication for protected HTML routes.
        Redirects to index or login as needed.
        """
        # Only protect HTML routes (except index)
        if (
            request.endpoint
            and request.endpoint.startswith("html.")
            and request.endpoint != "html.index"
        ):
            # Log the protected route
            logger.info(f"Protected route: {request.endpoint}")

            # Check for SignalWire credentials using the utility function
            if not has_sw_credentials():
                logger.warning(f"Authentication failed for {request.path}")
                flash("Please provide your SignalWire credentials first.")
                return redirect(url_for("html.index"))

            # Additional check for subscriber page
            if request.endpoint == "html.subscriber_page":
                # Use the utility function to check subscriber login
                if not is_subscriber_logged_in():
                    logger.warning(f"Subscriber login required for {request.path}")
                    flash("Please log in as a subscriber first.")
                    return redirect(url_for("html.login"))

    return app


def setup_app_config(app: Flask, **kwargs) -> None:
    """
    Set up additional app configuration, such as the public URL.

    Args:
        app (Flask): The Flask application instance.
        **kwargs: Additional configuration options.
    """
    public_url = kwargs.get("public_url")
    app.config["PUBLIC_URL"] = public_url

    # Log startup information
    logger.info(f"Application running at: {public_url}")
    logger.info(f"Debug mode: {'ON' if app.debug else 'OFF'}")
    logger.info(f"Running in Replit: {'YES' if REPLIT_ENV else 'NO'}")


def setup_public_url(port: int) -> str:
    """
    Set up public URL for the application, using ngrok tunneling if available.
    On Replit, use the REPLIT_DOMAINS environment variable to construct the public URL.

    Args:
        port (int): The port the application is running on

    Returns:
        str: The public URL for accessing the application
    """
    if REPLIT_ENV:
        replit_domains = os.environ.get("REPLIT_DOMAINS")
        if replit_domains:
            public_url = f"https://{replit_domains}"
            logger.info(f"Using Replit public URL: {public_url}")
            return public_url
        else:
            logger.warning("REPLIT_ENV is set but REPLIT_DOMAINS is not defined.")
    authtoken = os.environ.get("NGROK_AUTHTOKEN")
    if authtoken:
        try:
            logger.info("Setting up ngrok tunnel with provided authtoken")
            listener = ngrok.forward(f"localhost:{port}", authtoken=authtoken)
            public_url = listener.url()
            logger.info(f"ngrok tunnel established at: {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"Failed to establish ngrok tunnel: {e}")
    # Default fallback to localhost
    public_url = f"http://localhost:{port}"
    logger.info(f"Using local URL: {public_url}")
    return public_url


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Banner for the demo application
    print("\n" + "=" * 60)
    print("  LiveWire - SignalWire Demo Application")
    print("=" * 60)

    # Create and configure the application
    app = create_app()
    port = DEFAULT_PORT

    # Set debug based on environment variable
    app.debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    # Setup tunneling and get public URL
    public_url = setup_public_url(port)
    setup_app_config(app, public_url=public_url)

    logger.info(f"📱 Application URL: {public_url}")
    logger.info(f"🔧 Debug mode: {'ON' if app.debug else 'OFF'}")
    logger.info(f"🚀 Starting server on port {port}...")

    # Run the application
    app.run(port=port, host="0.0.0.0")

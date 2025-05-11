"""
Index route module.
Handles the landing page and SignalWire credential collection.
"""
from routes.html import html_bp
from flask import render_template, request, redirect, url_for, flash
import logging
import os
from utils.session_utils import set_sw_credentials, get_session_vars, set_swml_handler_info
from utils.session_utils import has_sw_credentials, clear_session, get_rest_client
from utils.signalwire_client import SignalWireAPIError

logger = logging.getLogger(__name__)

@html_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Landing page for collecting SignalWire credentials.
    If credentials already exist, redirects to call page.
    """
    # For GET requests, check if credentials exist and are valid
    if request.method == 'GET':
        has_credentials = has_sw_credentials()
        logger.info(f"Index page accessed. Has credentials: {has_credentials}")
        
        if has_credentials:
            logger.info("User already has credentials, redirecting to call page")
            return redirect(url_for('html.call_page'))
    
    # For POST requests, process form submission
    if request.method == 'POST':
        project_id = request.form.get('project_id', '').strip()
        auth_token = request.form.get('auth_token', '').strip()
        space_name = request.form.get('space_name', '').strip()
        
        # Validate inputs
        if not project_id or not auth_token or not space_name:
            missing = []
            if not project_id: missing.append('Project ID')
            if not auth_token: missing.append('Auth Token')
            if not space_name: missing.append('Space Name')
            
            flash(f"Missing required credentials: {', '.join(missing)}")
            return render_template('index.html')
        
        # Log input lengths
        logger.info(f"Processing SignalWire credentials - Project ID: {len(project_id)} chars, " +
                   f"Auth Token: {len(auth_token)} chars, Space Name: {space_name}")
        
        # Verify credentials by trying to create a REST client
        try:
            # Set credentials in session
            success = set_sw_credentials(project_id, auth_token, space_name)
            if not success:
                logger.error("Failed to set credentials in session")
                flash("Failed to save credentials. Please try again.")
                return render_template('index.html')
                
            # Try to create a client to verify credentials
            client = get_rest_client()
            if not client:
                logger.error("Failed to create REST client")
                flash("Failed to initialize SignalWire client. Please check your credentials.")
                clear_session()
                return render_template('index.html')
                
            # Credentials look good, let's continue
            logger.info("Credentials verified successfully")
                
        except SignalWireAPIError as e:
            logger.error(f"SignalWire API error validating credentials: {e.message}")
            flash(f"Invalid SignalWire credentials: {e.message}")
            clear_session()
            return render_template('index.html')
        except Exception as e:
            logger.exception(f"Unexpected error validating credentials: {e}")
            flash(f"An error occurred: {str(e)}")
            clear_session()
            return render_template('index.html')
            
        # Load existing SWML handler ID from file if it exists
        swml_id_path = os.path.join(os.getcwd(), 'swml_id.txt')
        if os.path.exists(swml_id_path):
            try:
                with open(swml_id_path, 'r') as f:
                    swml_id = f.read().strip()
                    if swml_id:
                        set_swml_handler_info(swml_id)
                        logger.info(f"Loaded SWML ID from file: {swml_id}")
            except Exception as e:
                logger.warning(f"Failed to load SWML ID from file: {e}")

        # Verify credentials and redirect
        if has_sw_credentials():
            logger.info("Credentials set successfully, redirecting to call page")
            return redirect(url_for('html.call_page'))
        else:
            logger.error("Failed to set credentials in session")
            flash("Failed to save credentials. Please try again.")
            return render_template('index.html')
    
    # For debugging
    logger.info("Rendering index page")
    return render_template('index.html') 
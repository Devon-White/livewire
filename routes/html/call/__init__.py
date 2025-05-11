"""
Call page route module.
Renders the call widget page for customers to call the AI agent.
"""
from routes.html import html_bp
from flask import render_template, redirect, url_for, flash
import logging
from utils.session_utils import get_session_vars, has_sw_credentials

logger = logging.getLogger(__name__)

@html_bp.route('/call')
def call_page():
    """
    Render the call page with SignalWire call widget.
    Validates all required session variables are present.
    """
    # Check for required session variables using session utilities
    session_vars = get_session_vars()
    has_credentials = has_sw_credentials()
    swml_id = session_vars.get('swml_id')
    
    # Verify we have all required data
    if not has_credentials or not swml_id:
        missing = []
        if not has_credentials:
            missing.append("SignalWire credentials")
        if not swml_id:
            missing.append("SWML Handler ID")
        
        logger.error(f"Missing required session variables: {', '.join(missing)}")
        flash(f"Missing required data: {', '.join(missing)}. Please enter your credentials again.")
        return redirect(url_for('html.index'))
    
    return render_template('call.html') 
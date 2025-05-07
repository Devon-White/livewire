from routes.html import html_bp
from flask import render_template, request, session, redirect, url_for, current_app
import logging
import os

logger = logging.getLogger(__name__)

@html_bp.route('/', methods=['GET', 'POST'])
def index():
    # If all credentials are present, redirect to /call
    if session.get('sw_project_id') and session.get('sw_auth_token') and session.get('sw_space_name'):
        return redirect(url_for('html.call_page'))

    if request.method == 'POST':
        logger.info(f"[INDEX] Form data: {request.form}")
        # Only process Stage 1 fields
        session['sw_project_id'] = request.form['project_id']
        session['sw_auth_token'] = request.form['auth_token']
        session['sw_space_name'] = request.form['space_name']
        session['sw_credentials_ok'] = True

        # NEW: Load swml_id from file if present
        swml_id_path = os.path.join(os.path.dirname(__file__), '../../../swml_id.txt')
        if os.path.exists(swml_id_path):
            with open(swml_id_path, 'r') as f:
                swml_id = f.read().strip()
                if swml_id:
                    session['swml_id'] = swml_id

        return redirect(url_for('html.call_page'))
    return render_template('index.html') 
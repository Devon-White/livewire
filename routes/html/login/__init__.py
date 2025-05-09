from routes.html import html_bp
from flask import render_template, request, redirect, url_for, session, current_app
from werkzeug.security import check_password_hash
import requests
import os
import logging
import base64
from stores.user_store import get_user_store
from utils.auth_decorators import require_sw_credentials
from stores.active_subscribers_store import set_active_subscriber
from utils.swml_utils import fetch_subscriber_address

@html_bp.route('/login', methods=['GET', 'POST'])
@require_sw_credentials(redirect_if_missing='html.index')
def login():
    error = None
    prefill_email = request.args.get('prefill_email', '')
    project_id = session.get('sw_project_id')
    auth_token = session.get('sw_auth_token')
    space_name = session.get('sw_space_name')
    if not (project_id and auth_token and space_name):
        error = 'SignalWire credentials missing from session. Please provide your credentials on the homepage.'
        return redirect(url_for('html.index'))
    auth = base64.b64encode(f"{project_id}:{auth_token}".encode()).decode()
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Basic {auth}'
    }
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = get_user_store().get(email)
        if user and check_password_hash(user['password_hash'], password):
            # Verify subscriber exists on SignalWire
            subscriber_id = user['subscriber_id']
            get_url = f"https://{space_name}.signalwire.com/api/fabric/resources/subscribers/{subscriber_id}"
            try:
                resp = requests.get(get_url, headers=headers)
                if not resp.ok:
                    error = 'Subscriber no longer exists. Please contact support.'
                else:
                    # Fetch and store address in active_subscribers store
                    address = fetch_subscriber_address(subscriber_id, project_id, auth_token, space_name)
                    if address:
                        set_active_subscriber(subscriber_id, address, session)
                    session['user_email'] = email
                    session['subscriber_ok'] = True
                    return redirect(url_for('html.subscriber_page'))
            except Exception as e:
                error = f"Error: {e}"
        else:
            error = 'Invalid email or password.'
    return render_template('login.html', error=error, prefill_email=prefill_email) 
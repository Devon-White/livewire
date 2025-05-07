from routes.html import html_bp
from flask import render_template, request, redirect, url_for, session, current_app
from werkzeug.security import check_password_hash
import requests
import os

from routes.html.signup import user_store

@html_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    prefill_email = request.args.get('prefill_email', '')
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = user_store.get(email)
        if user and check_password_hash(user['password_hash'], password):
            # Verify subscriber exists on SignalWire
            SIGNALWIRE_SPACE = os.getenv('SIGNALWIRE_SPACE')
            subscriber_id = user['subscriber_id']
            get_url = f"https://{SIGNALWIRE_SPACE}.signalwire.com/api/fabric/resources/subscribers/{subscriber_id}"
            headers = {
                'Accept': 'application/json',
                'Authorization': current_app.config['SIGNALWIRE_AUTH']
            }
            try:
                resp = requests.get(get_url, headers=headers)
                if not resp.ok:
                    error = 'Subscriber no longer exists. Please contact support.'
                else:
                    session['user_email'] = email
                    return redirect(url_for('html.subscriber_page'))
            except Exception as e:
                error = f"Error: {e}"
        else:
            error = 'Invalid email or password.'
    return render_template('login.html', error=error, prefill_email=prefill_email) 
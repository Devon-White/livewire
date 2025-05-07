from routes.html import html_bp
from flask import render_template, request, redirect, url_for, session, current_app
from werkzeug.security import generate_password_hash
import requests
import os
import logging

user_store = {}  # {email: {password_hash, subscriber_id}}

logger = logging.getLogger(__name__)

@html_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    prefill_email = ''
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        display_name = request.form.get('display_name', '').strip()
        job_title = request.form.get('job_title', '').strip()
        timezone = request.form.get('timezone', '').strip()
        country = request.form.get('country', '').strip()
        region = request.form.get('region', '').strip()
        company_name = request.form.get('company_name', '').strip()
        prefill_email = email
        # Confirm password check
        if password != confirm_password:
            error = 'Passwords do not match.'
        elif email in user_store:
            error = 'Email already registered.'
        else:
            SIGNALWIRE_SPACE = os.getenv('SIGNALWIRE_SPACE')
            api_url = f"https://{SIGNALWIRE_SPACE}.signalwire.com/api/fabric/resources/subscribers"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': current_app.config['SIGNALWIRE_AUTH']
            }
            # Try to find existing subscriber by email
            try:
                get_headers = headers.copy()
                get_headers.pop('Content-Type', None)
                resp = requests.get(api_url, headers=get_headers)
                subscriber = None
                subscriber_id = None
                if resp.ok:
                    for sub in resp.json().get('data', []):
                        if sub['subscriber']['email'].lower() == email:
                            subscriber = sub['subscriber']
                            subscriber_id = sub['id']
                            break
                # If not found, create new subscriber
                if not subscriber_id:
                    payload = {
                        "email": email,
                        "password": password,
                        "first_name": first_name,
                        "last_name": last_name,
                        "display_name": display_name,
                        "job_title": job_title,
                        "timezone": timezone,
                        "country": country,
                        "region": region,
                        "company_name": company_name
                    }
                    # Remove empty optional fields
                    payload = {k: v for k, v in payload.items() if v}
                    resp = requests.post(api_url, headers=headers, json=payload)
                    if not resp.ok:
                        try:
                            errors = resp.json().get('errors', [])
                            for err in errors:
                                if err.get('code') == 'invalid_parameter' and err.get('attribute') == 'password':
                                    error = err.get('message', 'Password is too short.')
                                    break
                            else:
                                error = f"Failed to create subscriber: {resp.text}"
                        except Exception:
                            error = f"Failed to create subscriber: {resp.text}"
                        return render_template('signup.html', error=error, email=prefill_email)
                    subscriber_id = resp.json().get('id')
                    if not subscriber_id:
                        error = 'No subscriber ID returned.'
                        return render_template('signup.html', error=error, email=prefill_email)
                    # Use form values for new subscriber
                    subscriber = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "display_name": display_name,
                        "job_title": job_title,
                        "timezone": timezone,
                        "country": country,
                        "region": region,
                        "company_name": company_name
                    }
                else:
                    # If found, check if info matches; update if needed
                    update_fields = {}
                    if subscriber.get('first_name', '') != first_name:
                        update_fields['first_name'] = first_name
                    if subscriber.get('last_name', '') != last_name:
                        update_fields['last_name'] = last_name
                    if subscriber.get('display_name', '') != display_name:
                        update_fields['display_name'] = display_name
                    if subscriber.get('job_title', '') != job_title:
                        update_fields['job_title'] = job_title
                    if subscriber.get('timezone', '') != timezone:
                        update_fields['timezone'] = timezone
                    if subscriber.get('country', '') != country:
                        update_fields['country'] = country
                    if subscriber.get('region', '') != region:
                        update_fields['region'] = region
                    if subscriber.get('company_name', '') != company_name:
                        update_fields['company_name'] = company_name
                    # Always update password
                    update_fields['password'] = password
                    if update_fields:
                        put_url = f"{api_url}/{subscriber_id}"
                        resp = requests.put(put_url, headers=headers, json=update_fields)
                        if not resp.ok:
                            error = f"Failed to update subscriber: {resp.text}"
                            return render_template('signup.html', error=error, email=prefill_email)
                # Store user
                user_store[email] = {
                    'password_hash': generate_password_hash(password),
                    'subscriber_id': subscriber_id,
                    'display_name': display_name,
                    'first_name': first_name,
                    'last_name': last_name
                }
                return redirect(url_for('html.login', prefill_email=email))
            except Exception as e:
                logger.exception("Exception during subscriber signup:")
                error = f"Error: {e}"
    return render_template('signup.html', error=error, email=prefill_email) 
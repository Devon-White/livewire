"""
Signup route module.
Handles new subscriber registration on SignalWire platform.
"""
from routes.html import html_bp
from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
import logging
from stores.user_store import get_user_store
from utils.session_utils import get_session_vars, get_rest_client
from utils.signalwire_client import SignalWireAPIError

logger = logging.getLogger(__name__)

@html_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle subscriber registration or update.
    Authentication for SignalWire credentials is handled by global middleware.
    """
    error = None
    prefill_email = ''
    
    # Get SignalWire credentials from session
    session_vars = get_session_vars()
    
    # Get client from session
    client = get_rest_client()
    if not client:
        flash('SignalWire client not initialized. Please provide your credentials on the homepage.')
        return redirect(url_for('html.index'))
    
    # Handle form submission
    if request.method == 'POST':
        # Extract form fields
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
        
        # Validate inputs
        if password != confirm_password:
            error = 'Passwords do not match.'
        elif email in get_user_store():
            error = 'Email already registered.'
        else:
            try:
                # Look up existing subscriber by email
                subscriber, subscriber_id = client.get_subscriber_by_email(email)
                
                if not subscriber_id:
                    # Create new subscriber if not found
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
                    
                    # Remove empty fields
                    payload = {k: v for k, v in payload.items() if v}
                    
                    try:
                        # Create subscriber
                        response = client.create_subscriber(payload)
                        subscriber_id = response.get('id')
                        if not subscriber_id:
                            error = 'No subscriber ID returned from API'
                            return render_template('signup.html', error=error, email=prefill_email)
                            
                        # Use form values for new subscriber info
                        subscriber_info = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "display_name": display_name
                        }
                        
                    except SignalWireAPIError as e:
                        error = f"Failed to create subscriber: {e.message}"
                        return render_template('signup.html', error=error, email=prefill_email)
                        
                else:
                    # Update existing subscriber if needed
                    update_fields = {}
                    if subscriber.get('first_name', '') != first_name and first_name:
                        update_fields['first_name'] = first_name
                    if subscriber.get('last_name', '') != last_name and last_name:
                        update_fields['last_name'] = last_name
                    if subscriber.get('display_name', '') != display_name and display_name:
                        update_fields['display_name'] = display_name
                    if subscriber.get('job_title', '') != job_title and job_title:
                        update_fields['job_title'] = job_title
                    if subscriber.get('timezone', '') != timezone and timezone:
                        update_fields['timezone'] = timezone
                    if subscriber.get('country', '') != country and country:
                        update_fields['country'] = country
                    if subscriber.get('region', '') != region and region:
                        update_fields['region'] = region
                    if subscriber.get('company_name', '') != company_name and company_name:
                        update_fields['company_name'] = company_name
                        
                    # Always update password
                    update_fields['password'] = password
                    
                    if update_fields:
                        # Update subscriber if changes are needed
                        try:
                            client.update_subscriber(subscriber_id, update_fields)
                        except SignalWireAPIError as e:
                            error = f"Failed to update subscriber: {e.message}"
                            return render_template('signup.html', error=error, email=prefill_email)
                    
                    # Use latest values for subscriber info
                    subscriber_info = {
                        "first_name": first_name or subscriber.get('first_name', ''),
                        "last_name": last_name or subscriber.get('last_name', ''),
                        "display_name": display_name or subscriber.get('display_name', '')
                    }
                
                if subscriber_id:
                    # Store user in local store
                    get_user_store()[email] = {
                        'password_hash': generate_password_hash(password),
                        'subscriber_id': subscriber_id,
                        'display_name': subscriber_info.get('display_name', ''),
                        'first_name': subscriber_info.get('first_name', ''),
                        'last_name': subscriber_info.get('last_name', '')
                    }
                    
                    # Redirect to login with email prefilled
                    return redirect(url_for('html.login', prefill_email=email))
                    
            except Exception as e:
                logger.exception(f"Error in signup: {e}")
                error = f"An unexpected error occurred: {str(e)}"
    
    # Render the signup form
    return render_template('signup.html', error=error, email=prefill_email) 
"""
Logout route module.
Handles user logout and session clearing.
"""
from routes.html import html_bp
from flask import redirect, url_for, flash
from stores.active_subscribers_store import set_inactive_subscriber
from utils.session_utils import get_session_vars, clear_session
from stores.user_store import get_user_store

@html_bp.route('/logout')
def logout():
    """
    Handle user logout.
    Marks the subscriber as inactive and clears the session.
    """
    try:
        # Get current user information from session
        session_vars = get_session_vars()
        email = session_vars.get('user_email')
        
        # Find subscriber ID from user store if email is available
        subscriber_id = None
        if email:
            user = get_user_store().get(email)
            if user:
                subscriber_id = user.get('subscriber_id')
        
        # Mark subscriber as inactive if we have an ID
        if subscriber_id:
            set_inactive_subscriber(subscriber_id)
            
        # Clear all session data
        clear_session()
        
        # Flash success message and redirect to login
        flash("You have been logged out successfully", "info")
        
    except Exception as e:
        # Log the error but still try to clear session and redirect
        from flask import current_app
        current_app.logger.exception(f"Error during logout: {e}")
        clear_session()
        
    return redirect(url_for('html.login')) 
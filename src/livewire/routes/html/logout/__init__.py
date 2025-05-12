"""
Logout route module.
Handles user logout and session clearing.
"""

from flask import flash, redirect, url_for

from livewire.routes.html import html_bp
from livewire.stores.active_subscribers_store import set_inactive_subscriber
from livewire.stores.user_store import get_user_store
from livewire.utils.session_utils import clear_session, get_session_vars


@html_bp.route("/logout")
def logout() -> str:
    """
    Handle user logout.
    Marks the subscriber as inactive and clears the session.

    Returns:
        str: Redirect response to the login page.
    """
    try:
        # Get current user information from session
        session_vars = get_session_vars()
        email = session_vars.get("user_email")

        # Find subscriber ID from user store if email is available
        subscriber_id = None
        if email:
            user = get_user_store().get(email)
            if user:
                subscriber_id = user.get("subscriber_id")

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

    return redirect(url_for("html.login"))

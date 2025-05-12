"""
Subscriber dashboard route module.
Renders the agent dashboard for subscribers to handle calls.
"""

import logging

from flask import flash, redirect, render_template, url_for

from livewire.routes.html import html_bp
from livewire.stores.user_store import get_user
from livewire.utils.session_utils import (clear_subscriber_login,
                                          get_session_vars,
                                          is_subscriber_logged_in)

logger = logging.getLogger(__name__)


@html_bp.route("/subscriber")
def subscriber_page() -> str:
    """
    Render the subscriber dashboard page.
    Authentication is handled by the global middleware.

    Returns:
        str: Rendered HTML for the subscriber dashboard or a redirect response.
    """
    try:
        # Get user information from session
        session_vars = get_session_vars()
        email = session_vars.get("user_email")

        # Log authentication state for debugging
        subscriber_ok = is_subscriber_logged_in()
        logger.info(
            f"Subscriber page accessed with email={email}, subscriber_ok={subscriber_ok}"
        )

        # Verify that we have an email and user is logged in as subscriber
        if not is_subscriber_logged_in():
            logger.error(f"Missing subscriber authentication: email={email}")
            # Reset flag and redirect
            clear_subscriber_login()
            flash("Please sign in as a subscriber first.")
            return redirect(url_for("html.login"))

        # Double-check that user exists in user store
        user = get_user(email)
        if not user:
            logger.error(f"User not found in user_store: {email}")
            # Reset flag and redirect
            clear_subscriber_login()
            flash("User not found. Please log in again.")
            return redirect(url_for("html.login"))

        # Determine display name (prioritize display_name field, fall back to first + last name)
        display_name = user.get("display_name") or (
            (user.get("first_name", "") + " " + user.get("last_name", "")).strip()
        )

        # If no name is available, use email address
        if not display_name:
            display_name = email

        # Render the template with user info
        return render_template(
            "pages/subscriber.html.jinja",
            display_name=display_name,
            email=email,
            user=user,
        )

    except Exception as e:
        logger.exception(f"Error rendering subscriber page: {e}")
        flash("An error occurred. Please try again.")
        return redirect(url_for("html.login"))

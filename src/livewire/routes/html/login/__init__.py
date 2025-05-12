"""
Login route module.
Handles subscriber authentication.
"""

import logging

from flask import flash, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash

from livewire.routes.html import html_bp
from livewire.stores.active_subscribers_store import set_active_subscriber
from livewire.stores.user_store import get_user
from livewire.utils.session_utils import (clear_subscriber_login,
                                          get_rest_client, get_session_vars,
                                          set_subscriber_login)
from livewire.utils.signalwire_client import SignalWireAPIError

logger = logging.getLogger(__name__)


@html_bp.route("/login", methods=["GET", "POST"])
def login() -> str:
    """
    Handle subscriber login requests.
    Authentication for SignalWire credentials is handled by global middleware.

    Returns:
        str: Rendered HTML for the login page or a redirect response.
    """
    # Clear any existing subscriber login status
    clear_subscriber_login()

    error = None
    prefill_email = request.args.get("prefill_email", "")

    # Get session variables
    session_vars = get_session_vars()
    project_id = session_vars.get("project_id")
    auth_token = session_vars.get("auth_token")
    space_name = session_vars.get("space_name")

    # Verify credentials again (should be handled by decorator but double-check)
    if not (project_id and auth_token and space_name):
        flash(
            "SignalWire credentials missing from session. Please provide your credentials on the homepage."
        )
        return redirect(url_for("html.index"))

    # Handle POST request (login form submission)
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate inputs
        if not email or not password:
            error = "Email and password are required"
        else:
            # Get user from store
            user = get_user(email)

            # Verify user exists and password is correct
            if not user:
                error = "User not found"
            elif not check_password_hash(user.get("password_hash", ""), password):
                error = "Invalid password"
            else:
                # Successful login - set session flag and redirect
                logger.info(f"Successful login for {email}")

                # Check if user has a subscriber ID
                subscriber_id = user.get("subscriber_id")
                if not subscriber_id:
                    error = "User is not a subscriber. Please sign up first."
                else:
                    # Set session flags
                    set_subscriber_login(email)

                    # Get client from session
                    client = get_rest_client()
                    if not client:
                        flash(
                            "SignalWire client not initialized. Please provide your credentials on the homepage."
                        )
                        return redirect(url_for("html.index"))

                    # Mark subscriber as active
                    try:
                        # Fetch subscriber address
                        address = client.fetch_subscriber_address(subscriber_id)
                        if address:
                            set_active_subscriber(subscriber_id, address)
                            logger.info(
                                f"Marked subscriber {subscriber_id} as active with address {address}"
                            )
                        else:
                            logger.warning(
                                f"Could not fetch address for subscriber {subscriber_id}"
                            )

                    except SignalWireAPIError as e:
                        logger.warning(
                            f"Error fetching subscriber address: {e.message}"
                        )

                    # Redirect to subscriber dashboard
                    flash("Login successful!", "success")
                    return redirect(url_for("html.subscriber_page"))

        if error:
            flash(error, "error")

    # Render login form
    return render_template("pages/login.html.jinja", prefill_email=prefill_email)

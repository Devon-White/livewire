"""
Signup route module.
Handles new subscriber registration on SignalWire platform.
"""

import logging

from flask import flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from livewire.routes.html import html_bp
from livewire.stores.user_store import get_user_store
from livewire.utils.form_utils import (build_subscriber_update_fields,
                                       build_user_store_entry,
                                       extract_signup_fields)
from livewire.utils.session_utils import get_rest_client, get_session_vars
from livewire.utils.signalwire_client import SignalWireAPIError

logger = logging.getLogger(__name__)


@html_bp.route("/signup", methods=["GET", "POST"])
def signup() -> str:
    """
    Handle subscriber registration or update.
    Authentication for SignalWire credentials is handled by global middleware.

    Returns:
        str: Rendered HTML for the signup page or a redirect response.
    """
    error = None
    prefill_email = ""

    # Get SignalWire credentials from session
    session_vars = get_session_vars()

    # Get client from session
    client = get_rest_client()
    if not client:
        flash(
            "SignalWire client not initialized. Please provide your credentials on the homepage."
        )
        return redirect(url_for("html.index"))

    # Handle form submission
    if request.method == "POST":
        # Extract and clean form fields
        form_data = extract_signup_fields(request.form)
        email = form_data["email"].lower()
        password = form_data["password"]
        confirm_password = form_data["confirm_password"]
        prefill_email = email
        # Validate inputs
        if password != confirm_password:
            error = "Passwords do not match."
        elif email in get_user_store():
            error = "Email already registered."
        else:
            try:
                # Look up existing subscriber by email
                subscriber, subscriber_id = client.get_subscriber_by_email(email)

                if not subscriber_id:
                    # Create new subscriber if not found
                    payload = {
                        k: v
                        for k, v in form_data.items()
                        if k != "confirm_password" and v
                    }
                    try:
                        # Create subscriber
                        response = client.create_subscriber(payload)
                        subscriber_id = response.get("id")
                        if not subscriber_id:
                            error = "No subscriber ID returned from API"
                            return render_template(
                                "signup.html.jinja", error=error, email=prefill_email
                            )
                        subscriber_info = {
                            "first_name": form_data["first_name"],
                            "last_name": form_data["last_name"],
                            "display_name": form_data["display_name"],
                        }
                    except SignalWireAPIError as e:
                        error = f"Failed to create subscriber: {e.message}"
                        return render_template(
                            "signup.html.jinja", error=error, email=prefill_email
                        )
                else:
                    # Update existing subscriber if needed
                    update_fields = build_subscriber_update_fields(
                        subscriber, form_data
                    )
                    if update_fields:
                        try:
                            client.update_subscriber(subscriber_id, update_fields)
                        except SignalWireAPIError as e:
                            error = f"Failed to update subscriber: {e.message}"
                            return render_template(
                                "signup.html.jinja", error=error, email=prefill_email
                            )
                    subscriber_info = {
                        "first_name": form_data["first_name"]
                        or subscriber.get("first_name", ""),
                        "last_name": form_data["last_name"]
                        or subscriber.get("last_name", ""),
                        "display_name": form_data["display_name"]
                        or subscriber.get("display_name", ""),
                    }
                if subscriber_id:
                    # Store user in local store
                    get_user_store()[email] = build_user_store_entry(
                        form_data, subscriber_id
                    )
                    # Redirect to login with email prefilled
                    return redirect(url_for("html.login", prefill_email=email))
            except Exception as e:
                logger.exception(f"Error in signup: {e}")
                error = f"An unexpected error occurred: {str(e)}"

    # Render the signup form
    return render_template("pages/signup.html.jinja", error=error, email=prefill_email)

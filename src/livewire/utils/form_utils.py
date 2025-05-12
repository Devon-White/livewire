"""
Form utilities for DRY signup/login logic.
"""

from typing import Any, Dict

from werkzeug.security import generate_password_hash


def extract_signup_fields(form: Any) -> Dict[str, str]:
    """
    Extract and clean all relevant signup fields from a form object.

    Args:
        form (Any): The request.form object

    Returns:
        Dict[str, str]: Cleaned field values
    """
    fields = [
        "email",
        "password",
        "confirm_password",
        "first_name",
        "last_name",
        "display_name",
        "job_title",
        "timezone",
        "country",
        "region",
        "company_name",
    ]

    return {
        field: (
            form.get(field, "").strip()
            if field != "password" and field != "confirm_password"
            else form.get(field, "")
        )
        for field in fields
        if field in form
    }


def build_subscriber_update_fields(
    subscriber: Dict[str, Any], form_data: Dict[str, str]
) -> Dict[str, str]:
    """
    Build a dict of fields to update for a subscriber based on form data.

    Args:
        subscriber (Dict[str, Any]): Existing subscriber data
        form_data (Dict[str, str]): Cleaned form data

    Returns:
        Dict[str, str]: Fields to update
    """
    update_fields = {}
    for field in [
        "first_name",
        "last_name",
        "display_name",
        "job_title",
        "timezone",
        "country",
        "region",
        "company_name",
    ]:
        if form_data.get(field) and subscriber.get(field, "") != form_data[field]:
            update_fields[field] = form_data[field]
    # Always update password
    update_fields["password"] = form_data["password"]
    return update_fields


def build_user_store_entry(
    form_data: Dict[str, str], subscriber_id: str
) -> Dict[str, str]:
    """
    Build a user store entry from form data and subscriber ID.

    Args:
        form_data (Dict[str, str]): Cleaned form data
        subscriber_id (str): The subscriber's ID

    Returns:
        Dict[str, str]: User store entry
    """
    return {
        "password_hash": generate_password_hash(form_data["password"]),
        "subscriber_id": subscriber_id,
        "display_name": form_data.get("display_name", ""),
        "first_name": form_data.get("first_name", ""),
        "last_name": form_data.get("last_name", ""),
    }

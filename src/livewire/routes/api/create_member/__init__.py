"""
Create member API endpoint.
Handles creation of new members during calls and notifies AI agent.
"""

import logging
import random

from flask import request

from livewire.stores.call_info_store import get_call_info_store
from livewire.stores.customer_store import add_customer, get_customer_store
from livewire.utils.api_utils import (api_error, api_success, validate_email,
                                      validate_json_request)
from livewire.utils.session_utils import (get_current_call_id, get_rest_client,
                                          get_session_vars,
                                          set_current_call_id)
from livewire.utils.signalwire_client import SignalWireAPIError

from .. import api_bp

logger = logging.getLogger(__name__)

# Constants
MEMBER_ID_MIN = 100000
MEMBER_ID_MAX = 999999


def get_current_call_id_from_sources():
    """Get the current call ID from various sources"""
    # Try from JSON data or session
    call_id = None

    # Try from JSON data
    if request.is_json:
        call_id = request.json.get("call_id")

    # Try from session using utility function
    if not call_id:
        call_id = get_current_call_id()

    # Try from call_info_store as last resort
    if not call_id:
        call_info_store = get_call_info_store()
        if call_info_store:
            call_id = next(iter(call_info_store.keys()), None)

    return call_id


def generate_unique_member_id():
    """Generate a unique member ID not already in the store"""
    store = get_customer_store()
    while True:
        member_id = f"M{random.randint(MEMBER_ID_MIN, MEMBER_ID_MAX)}"
        if member_id not in store:
            return member_id


def format_member_data_prompt(member_data, member_id):
    """Format member data for AI prompt"""
    prompt_lines = [
        f"A new member has been created. Their member ID is: {member_id}",
        "They submitted the following information:",
        "",
    ]
    for k, v in member_data.items():
        prompt_lines.append(f"- {k}: {v}")
    return "\n".join(prompt_lines)


@api_bp.route("/api/create_member", methods=["POST"])
@validate_json_request(
    required_fields=[
        "first_name",
        "last_name",
        "email",
        "password",
        "confirm_password",
    ],
    field_types={
        "first_name": str,
        "last_name": str,
        "email": str,
        "password": str,
        "confirm_password": str,
        "phone": str,  # Optional
        "display_name": str,  # Optional
        "job_title": str,  # Optional
        "company_name": str,  # Optional
        "call_id": str,  # Optional, added by JS if available
    },
    custom_validators={"email": validate_email},
)
def create_member():
    try:
        # 1. Get validated fields
        first_name = request.json["first_name"]
        last_name = request.json["last_name"]
        email = request.json["email"]
        password = request.json["password"]

        # Optional fields
        phone = request.json.get("phone", "")
        display_name = request.json.get("display_name", "")
        job_title = request.json.get("job_title", "")
        company_name = request.json.get("company_name", "")

        # 2. Get call_id (either from request or session)
        call_id = request.json.get("call_id")
        if not call_id:
            call_id = get_current_call_id_from_sources()

        if not call_id:
            return api_error(
                "No call_id found for create_member operation", log_level="error"
            )

        # 3. Prepare form data
        form_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
        }

        # Add optional fields if present
        if phone:
            form_data["phone"] = phone
        if display_name:
            form_data["display_name"] = display_name
        if job_title:
            form_data["job_title"] = job_title
        if company_name:
            form_data["company_name"] = company_name

        # 4. Generate unique member_id and add to store
        member_id = generate_unique_member_id()
        member_data = {"member_id": member_id, **form_data, "premium_member": True}
        add_customer(member_data)

        # 5. Format prompt for AI
        prompt = format_member_data_prompt(form_data, member_id)

        # 6. Send commands to SignalWire API
        try:
            client = get_rest_client()
            if not client:
                return api_error("SignalWire client not initialized", 400)

            # Notify AI about new member
            client.notify_ai_about_new_member(call_id, prompt)

            # Store the call ID in the session
            set_current_call_id(call_id)

        except SignalWireAPIError as e:
            logger.exception(f"SignalWire API error: {e.message}")
            return api_error(
                "SignalWire API error",
                500,
                log_level="error",
                details={"message": e.message, "status_code": e.status_code},
            )

        return api_success({"member_id": member_id}, "Member created successfully")

    except Exception as e:
        logger.exception("Unexpected error in create_member")
        return api_error(
            "Unexpected error in create_member operation",
            500,
            log_level="error",
            details={"error": str(e)},
        )

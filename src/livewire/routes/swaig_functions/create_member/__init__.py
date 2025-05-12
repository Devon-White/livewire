"""
Create Member SWAIG function.
Handles the creation of a new member via form submission during a call.
"""

import logging
import os

from signalwire_swaig import SWAIGArgument, SWAIGFunctionProperties

from livewire.routes import swaig
from livewire.utils.swml_utils import load_swml_with_vars

logger = logging.getLogger(__name__)

# Load YAML template for response
create_member_yaml = os.path.join(os.path.dirname(__file__), "create_member.yaml")


@swaig.endpoint(
    "The function to execute when the user claims they would like to be a member.",
    SWAIGFunctionProperties(
        fillers={
            "default": [
                "Thank you, I will send you a form to fill out to become a member now. You should see it on your screen shortly.",
                "Excellent! I'm glad to hear you are interested, you should see a form on your screen shortly.",
            ]
        }
    ),
    create_member=SWAIGArgument(
        type="boolean", required=True, description="Whether to create a member"
    ),
)
def create_member(create_member: bool, **kwargs):
    """
    Send a form to the user to become a member.

    Args:
        create_member: Boolean indicating if the user wants to become a member
        **kwargs: Additional arguments from SWAIG

    Returns:
        str or tuple: Simple result string if rejected, or (result_text, swml_response) if accepted
    """
    # Get call context from kwargs if available
    call_id = kwargs.get("meta_data", {}).get("call_id", "unknown")
    logger.info(
        f"create_member called for call {call_id}: create_member={create_member}"
    )

    # If user doesn't want to be a member, just return a result
    if not create_member:
        result = "The user does not want to be a member."
        logger.info(f"Call {call_id}: {result}")
        return result

    # Load SWML with form for member creation
    try:
        swml = load_swml_with_vars(swml_file=create_member_yaml)
        result = "The user has informed us they would like to become a member. Sending form now."
        logger.info(f"Call {call_id}: {result}")
        return result, swml
    except Exception as e:
        logger.exception(f"Error loading create_member SWML: {e}")
        return "Error sending member form, please try again."

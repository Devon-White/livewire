"""
Verify Customer SWAIG function.
Verifies if a given member ID exists in the customer store.
"""
import os
from routes import swaig
from signalwire_swaig import SWAIGArgument, SWAIGFunctionProperties
from utils.swml_utils import load_swml_with_vars
import logging
from stores.customer_store import get_customer

logger = logging.getLogger(__name__)

# Load YAML files for responses
customer_verified_yaml = os.path.join(os.path.dirname(__file__), "customer_verified.yaml")
customer_not_found_yaml = os.path.join(os.path.dirname(__file__), "customer_not_found.yaml")

@swaig.endpoint(
    'The function to execute when we need to verify the customer account ID provided.',
    SWAIGFunctionProperties(
        fillers={
            "default": [
                "Thank you, let me verify the member id you provided.",
                "Excellent, verifying your member id now, one second please."
            ]
        }
    ),
    member_id=SWAIGArgument(type="string", required=True, description="The member ID to verify")
)
def verify_customer_id(member_id: str, **kwargs):
    """
    Verify if a member ID exists in the customer store.
    
    Args:
        member_id: The member ID to verify
        **kwargs: Additional arguments from SWAIG
        
    Returns:
        tuple: (result_text, swml_response) if verified, or result_text if not verified
    """
    logger.info(f"Verifying customer data for {member_id}")
    
    # Get customer data using the improved utility function
    customer_data = get_customer(member_id)
    
    if customer_data:
        # Member verified - return success message and SWML response
        swml = load_swml_with_vars(swml_file=customer_verified_yaml)
        result = f"Customer data verified for {member_id}. Welcome the user by {customer_data['first_name']} {customer_data['last_name']}."
        logger.info(f"Customer data verified for {member_id}.")
        return result, swml
    else:
        # Member not found - return failure message
        result = f"Customer data not found for {member_id}. The user needs to provide a valid member id."
        logger.info(f"Customer data not found for {member_id}.")
        return result
import os
from routes import swaig
from signalwire_swaig import SWAIGArgument
from utils.swml_utils import load_swml_with_vars
import logging

logger = logging.getLogger(__name__)

customer_verified_yaml = os.path.join(os.path.dirname(__file__), "customer_verified.yaml")
customer_not_found_yaml = os.path.join(os.path.dirname(__file__), "customer_not_found.yaml")

def get_customer_data(member_id):
    CUSTOMER_DATA = [
        {
            "member_id": "AB12345",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "premium_member": True
        }
    ]
    for customer in CUSTOMER_DATA:
        if customer["member_id"].lower() == member_id.lower():
            return customer
    return None


@swaig.endpoint(
    'The function to execute when we need to verify the customer account ID provided.',
    member_id=SWAIGArgument(type="string", required=True, description="The member ID to verify")
)
def verify_customer_id(member_id: str, **kwargs):
    logger.info(f"Verifying customer data for {member_id}")
    logger.info(kwargs)
    customer_data = get_customer_data(member_id)
    if customer_data:
        swml = load_swml_with_vars(
            swml_file=customer_verified_yaml
        )
        result = f"Customer data verified for {member_id}. Welcome the user by {customer_data['first_name']} {customer_data['last_name']}."
        logger.info(result)
        return result, swml
    else:
        swml = load_swml_with_vars(
            swml_file=customer_not_found_yaml,
            member_id=member_id
        )
        result = f"Customer data not found for {member_id}. The user needs to try again."
        logger.info(result)
        return result, swml
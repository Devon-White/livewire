import os
from routes import swaig
from signalwire_swaig import SWAIGArgument, SWAIGFunctionProperties
from utils.swml_utils import load_swml_with_vars
import logging
from stores.customer_store import get_customer_store

logger = logging.getLogger(__name__)

customer_verified_yaml = os.path.join(os.path.dirname(__file__), "customer_verified.yaml")
customer_not_found_yaml = os.path.join(os.path.dirname(__file__), "customer_not_found.yaml")

def get_customer_data(member_id):
    store = get_customer_store()
    for cid, customer in store.items():
        if cid.lower() == member_id.lower():
            return customer
    return None


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
    logger.info(f"Verifying customer data for {member_id}")
    customer_data = get_customer_data(member_id)
    if customer_data:
        swml = load_swml_with_vars(
            swml_file=customer_verified_yaml
        )
        result = f"Customer data verified for {member_id}. Welcome the user by {customer_data['first_name']} {customer_data['last_name']}."
        logger.info(f"Customer data verified for {member_id}.")
        return result, swml
    else:
        result = f"Customer data not found for {member_id}. The user needs to provide a valid member id."
        logger.info(f"Customer data not found for {member_id}.")
        return result
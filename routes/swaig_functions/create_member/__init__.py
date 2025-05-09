import os
from routes import swaig
from signalwire_swaig import SWAIGArgument, SWAIGFunctionProperties
from utils.swml_utils import load_swml_with_vars
from flask import session
import logging
import base64

logger = logging.getLogger(__name__)

create_member_yaml = os.path.join(os.path.dirname(__file__), "create_member.yaml")

@swaig.endpoint(
    'The function to execute when the user claims they would like to be a member.',
    SWAIGFunctionProperties(
        fillers={
            "default": [
                "Thank you, i will send you a form to fill out to become a member now. You should see it on your screen shortly.",
                "Excellent! I'm glad to hear you are interested, you should see a form on your screen shortly.",

            ]
        }
        ),
    create_member=SWAIGArgument(type="boolean", required=True, description="Whether to create a member"),
)
def create_member(create_member: bool, **kwargs):

    if not create_member:
        result = "The user does not want to be a member."
        logger.info(result)
        return result
    
    swml = load_swml_with_vars(
        swml_file=create_member_yaml
                        )
    result = f"The user has informed us they would like to become a member. Sending form now."
    logger.info(result)
    return result, swml 
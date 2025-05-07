import os
from routes import swaig
from signalwire_swaig import SWAIGArgument, SWAIGFunctionProperties
from utils.swml_utils import load_swml_with_vars
from flask import current_app
import logging
from stores.call_info_store import get_call_info_store

logger = logging.getLogger(__name__)

send_user_info_yaml = os.path.join(os.path.dirname(__file__), "send_user_info.yaml")

@swaig.endpoint(
    'The function to execute when we need to send the user info to the client.',
    SWAIGFunctionProperties(
        active=False,
        fillers={
            "default": [
                "Thank you ${args.first_name} ${args.last_name}, I am transferring you to the next available agent.",

            ]
        }
        ),
    first_name=SWAIGArgument(type="string", required=True, description="The user's first name"),
    last_name=SWAIGArgument(type="string", required=True, description="The user's last name"),
    summary=SWAIGArgument(type="string", required=True, description="The user's summary"),
)
def send_user_info(first_name: str, last_name: str, summary: str, **kwargs):

    call_id = kwargs.get('meta_data', {}).get('call_id')
    status_callback_url = f"{current_app.config['PUBLIC_URL']}/api/call_status"
    logger.info(f"Sending user info: {first_name} {last_name} {summary} {call_id}")
    swml = load_swml_with_vars(
        swml_file=send_user_info_yaml,
        first_name=first_name,
        last_name=last_name,
        subscriber_address='/private/devon-white',
        summary=summary,
        status_callback_url=status_callback_url
        )
    if call_id:
        get_call_info_store()[call_id] = {
            'first_name': first_name,
            'last_name': last_name,
            'summary': summary
        }
        logger.info(f"Stored call info for call_id {call_id}: {get_call_info_store()[call_id]}")
    else:
        logger.warning("No call_id found to store call info!")
    result = f"Sending form to the user now"
    logger.info(result)
    return result, swml 
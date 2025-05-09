import os
from routes import swaig
from signalwire_swaig import SWAIGArgument, SWAIGFunctionProperties
from utils.swml_utils import load_swml_with_vars
from flask import current_app, session
import logging
from stores.call_info_store import get_call_info_store, set_call_info
from stores.active_subscribers_store import get_active_subscribers_by_project
import yaml

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

    call_info = get_call_info_store().get(call_id, {})
    context = call_info.get('context', {})
    project_id = context.get('project_id')

    try:
        if not project_id:
            raise ValueError('project_id must be present in call context')
        logger.info(f"Looking for active subscribers in project: {project_id}")
        active_subs = get_active_subscribers_by_project(project_id)
        logger.info(f"Found {len(active_subs)} active subscribers.")
        addresses = [v['address'] for v in active_subs.values() if v.get('address')]
        logger.info(f"Active subscriber addresses for transfer: {len(addresses)} addresses.")
    except Exception as e:
        logger.error(f"Error fetching active subscribers: {e}")
        addresses = []

    # Build the parallel block as a YAML-formatted string
    parallel_block = yaml.dump([{'to': addr} for addr in addresses], default_flow_style=True).strip()

    swml = load_swml_with_vars(
        swml_file=send_user_info_yaml,
        first_name=first_name,
        last_name=last_name,
        status_callback_url=status_callback_url,
        parallel_block=parallel_block
    )

    logger.info(f"SWML loaded for call_id {call_id}.")

    try:
        logger.info('Final SWML for transfer (not shown for brevity)')
    except Exception as e:
        logger.error('Error dumping SWML for transfer: %s', e)

    if call_id:
        set_call_info(call_id, {
            'first_name': first_name,
            'last_name': last_name,
            'summary': summary
        })
        logger.info(f"Stored call info for call_id {call_id}.")
    else:
        logger.warning("No call_id found to store call info!")
    result = f"Sending form to the user now"
    logger.info(result)
    logger.info(f"SWML after load_swml_with_vars: {swml}")
    return result, swml 
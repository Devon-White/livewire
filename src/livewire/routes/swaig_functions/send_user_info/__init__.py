"""
Send User Info SWAIG function.
Transfers the call to available subscriber agents with user information.
"""

import logging
import os

import yaml
from flask import current_app
from signalwire_swaig import SWAIGArgument, SWAIGFunctionProperties

from livewire.routes import swaig
from livewire.stores.active_subscribers_store import \
    get_active_subscribers_by_project
from livewire.stores.call_info_store import get_call_context, set_call_info
from livewire.utils.swml_utils import load_swml_with_vars

logger = logging.getLogger(__name__)

# Load YAML template for response
send_user_info_yaml = os.path.join(os.path.dirname(__file__), "send_user_info.yaml")


@swaig.endpoint(
    "The function to execute when we need to send the user info to the client.",
    SWAIGFunctionProperties(
        active=False,
        fillers={
            "default": [
                "Thank you ${args.first_name} ${args.last_name}, I am transferring you to the next available agent.",
            ]
        },
    ),
    first_name=SWAIGArgument(
        type="string", required=True, description="The user's first name"
    ),
    last_name=SWAIGArgument(
        type="string", required=True, description="The user's last name"
    ),
    summary=SWAIGArgument(
        type="string", required=True, description="The user's summary"
    ),
)
def send_user_info(first_name: str, last_name: str, summary: str, **kwargs):
    """
    Transfer the call to available subscriber agents with user information.
    """
    try:
        # Extract call information from request metadata
        call_id = kwargs.get("meta_data", {}).get("call_id")
        logger.info(f"[send_user_info] Called with first_name={first_name}, last_name={last_name}, summary={summary}, call_id={call_id}")
        logger.info(f"[send_user_info] Input kwargs: {kwargs}")

        # Set up callback URL for status updates
        status_callback_url = f"{current_app.config['PUBLIC_URL']}/api/call_status"

        # Get project ID from call context
        context = get_call_context(call_id) if call_id else {}
        logger.info(f"[send_user_info] Call context: {context}")
        project_id = context.get("project_id")
        logger.info(f"[send_user_info] Project ID: {project_id}")

        # Find active subscribers for transfer
        addresses = []
        if project_id:
            try:
                logger.info(f"[send_user_info] Looking for active subscribers in project: {project_id}")
                active_subs = get_active_subscribers_by_project(project_id)
                logger.info(f"[send_user_info] Found {len(active_subs)} active subscribers: {active_subs}")

                # Extract addresses from active subscribers
                addresses = [v["address"] for v in active_subs.values() if v.get("address")]
                logger.info(f"[send_user_info] Found {len(addresses)} subscriber addresses for transfer: {addresses}")
            except Exception as e:
                logger.exception(f"[send_user_info] Error fetching active subscribers: {e}")
        else:
            logger.warning("[send_user_info] No project_id found in call context, cannot find subscribers for transfer")

        # Build parallel transfer block for SWML
        try:
            parallel_block = yaml.dump(
                [{"to": addr} for addr in addresses], default_flow_style=True
            ).strip()
            logger.info(f"[send_user_info] Parallel block for SWML: {parallel_block}")
        except Exception as e:
            logger.exception(f"[send_user_info] Error building parallel block: {e}")
            parallel_block = ''

        # Load and populate SWML template
        try:
            swml = load_swml_with_vars(
                swml_file=send_user_info_yaml,
                first_name=first_name,
                last_name=last_name,
                status_callback_url=status_callback_url,
                parallel_block=parallel_block,
            )
            logger.info(f"[send_user_info] Loaded SWML template successfully.")
        except Exception as e:
            logger.exception(f"[send_user_info] Error loading SWML template: {e}")
            swml = ''

        # Store call information for reference by subscriber dashboard
        if call_id:
            try:
                set_call_info(
                    call_id,
                    {"first_name": first_name, "last_name": last_name, "summary": summary},
                )
                logger.info(f"[send_user_info] Stored call info for call_id {call_id}")
            except Exception as e:
                logger.exception(f"[send_user_info] Error storing call info: {e}")
        else:
            logger.warning("[send_user_info] No call_id found to store call info!")

        # Return response and SWML
        result = f"Transferring to available agents"
        logger.info(f"[send_user_info] Returning result and swml.")
        return result, swml
    except Exception as e:
        logger.exception(f"[send_user_info] Exception in send_user_info: {e}")
        raise

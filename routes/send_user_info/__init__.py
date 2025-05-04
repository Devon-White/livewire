import os
from routes import swaig
from swaig import SWAIGArgument, SWAIGFunctionProperties
from setup import load_swml_with_vars


send_user_info_yaml = os.path.join(os.path.dirname(__file__), "send_user_info.yaml")

@swaig.endpoint(
    'The function to execute when we need to send the user info to the client.',
    SWAIGFunctionProperties(active=False),
    first_name=SWAIGArgument(type="string", required=True, description="The user's first name"),
    last_name=SWAIGArgument(type="string", required=True, description="The user's last name"),
    summary=SWAIGArgument(type="string", required=True, description="The user's summary")
)
def send_user_info(first_name: str, last_name: str, summary: str, **kwargs):
    print(f"Sending user info: {first_name} {last_name}")
    swml = load_swml_with_vars(
        swml_file=send_user_info_yaml,
        first_name=first_name,
        last_name=last_name
        )
    result = f"Sending the user info to the client"
    print(result)
    return result, swml 
import json
import yaml
import logging
import requests
import base64

def load_swml_with_vars(swml_file, **kwargs):
    try:
        with open(swml_file, 'r') as f:
            content = f.read()
        # Inject variables into the file content
        content = content.format(**kwargs)
        if swml_file.endswith(('.yml', '.yaml')):
            return yaml.safe_load(content)
        else:
            return json.loads(content)
    except Exception as e:
        logging.error(f"Error loading {swml_file} with vars: {e}")
        return None 

def fetch_subscriber_address(subscriber_id, project_id, auth_token, space_name):
    """
    Fetch the audio address for a subscriber from SignalWire, trimming everything after '?'.
    Returns the address string or None on error.
    """
    api_base = f"https://{space_name}.signalwire.com/api/fabric/resources/subscribers"
    auth = base64.b64encode(f"{project_id}:{auth_token}".encode()).decode()
    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {auth}"
    }
    addresses_url = f"{api_base}/{subscriber_id}/addresses"
    try:
        resp = requests.get(addresses_url, headers=headers)
        if not resp.ok:
            return None
        data = resp.json().get('data', [])
        if not data:
            return None
        channels = data[0].get('channels') or data[0].get('channel')
        if not channels or 'audio' not in channels:
            return None
        audio_path = channels['audio']
        address = audio_path.split('?')[0]
        return address
    except Exception:
        return None 
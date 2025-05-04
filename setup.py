import os
import json
import requests
import base64
import logging
from dotenv import load_dotenv
import yaml


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

SIGNALWIRE_SPACE = os.getenv("SIGNALWIRE_SPACE")
SIGNALWIRE_PROJECT = os.getenv("SIGNALWIRE_PROJECT")
SIGNALWIRE_TOKEN = os.getenv("SIGNALWIRE_TOKEN")
API_BASE = f"https://{SIGNALWIRE_SPACE}.swire.io/api/fabric/resources/external_swml_handlers"
ID_FILE = "swml_id.txt"

print(SIGNALWIRE_SPACE, SIGNALWIRE_PROJECT, SIGNALWIRE_TOKEN)

BASE64_ENCODED_CREDENTIALS = base64.b64encode(f"{SIGNALWIRE_PROJECT}:{SIGNALWIRE_TOKEN}".encode()).decode()

def get_stored_id():
    if os.path.exists(ID_FILE):
        with open(ID_FILE, 'r') as f:
            return f.read().strip()
    return None

def store_id(swml_id):
    with open(ID_FILE, 'w') as f:
        f.write(swml_id)

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

def create_swml_handler(headers, payload):
    response = requests.post(API_BASE, headers=headers, data=json.dumps(payload))
    if response.ok:
        data = response.json()
        swml_id = data.get('id')
        if swml_id:
            store_id(swml_id)
            logging.info(f"Successfully created External SWML Handler with ID: {swml_id}")
        else:
            logging.warning("External SWML Handler created but no ID returned in response.")
    else:
        logging.error(f"Failed to create External SWML Handler. Status code: {response.status_code}, Response: {response.text}")
    return response

def update_swml_script(public_url):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Basic ' + BASE64_ENCODED_CREDENTIALS
    }
    payload = {
        "name": "LiveWire",
        "primary_request_url": f"{public_url.rstrip('/')}/swml"
    }
    swml_id = get_stored_id()

    if swml_id:
        # Try to update existing External SWML Handler
        url = f"{API_BASE}/{swml_id}"
        response = requests.patch(url, headers=headers, data=json.dumps(payload))
        logging.info(f"Update response: {response.status_code} {response.text}")
        if not response.ok:
            logging.warning(f"Failed to update External SWML Handler with ID {swml_id}. Creating a new handler.")
            response = create_swml_handler(headers, payload)
        else:
            logging.info(f"Successfully updated External SWML Handler with ID: {swml_id}")
    else:
        # No ID file, create new External SWML Handler
        response = create_swml_handler(headers, payload)
    return response
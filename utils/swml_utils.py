import json
import yaml
import logging

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
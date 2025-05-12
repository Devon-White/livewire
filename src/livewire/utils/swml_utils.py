"""
SWML utility functions for the LiveWire demo app.
Provides helpers for loading and formatting SWML files.
"""

import json
import logging
from typing import Any, Dict, Optional

import yaml


def load_swml_with_vars(swml_file: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
    """
    Load a SWML file and format with variables.

    Args:
        swml_file (str): Path to the SWML file
        **kwargs: Variables to format into the file

    Returns:
        Optional[Dict[str, Any]]: Parsed SWML content or None on error
    """
    try:
        with open(swml_file, "r") as f:
            content = f.read()
        # Inject variables into the file content
        content = content.format(**kwargs)
        if swml_file.endswith((".yml", ".yaml")):
            return yaml.safe_load(content)
        else:
            return json.loads(content)
    except Exception as e:
        logging.error(f"Error loading {swml_file} with vars: {e}")
        return None


# Note: The fetch_subscriber_address function has been moved to utils/signalwire_client.py
# Please use SignalWireClient.fetch_subscriber_address() instead.

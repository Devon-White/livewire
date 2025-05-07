from .. import api_bp
from flask import jsonify, current_app
from utils.swml_utils import load_swml_with_vars
import os
import logging

logger = logging.getLogger(__name__)

main_swml_file = os.path.join(os.path.dirname(__file__), "main_swml.yaml")

@api_bp.route('/api/swml', methods=['POST', 'GET'])
def swml():
    try:
        public_url = current_app.config['PUBLIC_URL']  # This should be set appropriately, possibly via config or import
        swml_data = load_swml_with_vars(swml_file=main_swml_file, public_url=public_url)
        logger.info(swml_data)
        return swml_data, 200
    except Exception as e:
        return jsonify({"error": f"Could not read SWML file: {e}"}), 500
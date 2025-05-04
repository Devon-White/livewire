from flask import Blueprint, render_template
from setup import load_swml_with_vars
import os

main_bp = Blueprint('main', __name__)

main_swml_file = os.path.join("swml_responses", "main_swml.yaml")
public_url = None

def set_public_url(url):
    global public_url
    public_url = url

@main_bp.route('/swml', methods=['POST', 'GET'])
def swml():
    try:
        swml_data = load_swml_with_vars(swml_file=main_swml_file, public_url=public_url)
        print(swml_data)
        return swml_data, 200
    except Exception as e:
        return {"error": f"Could not read SWML file: {e}"}, 500

@main_bp.route('/')
def index():
    return render_template('index.html') 
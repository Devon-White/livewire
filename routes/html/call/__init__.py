from routes.html import html_bp
from flask import render_template
from utils.auth_decorators import require_sw_credentials

@html_bp.route('/call')
@require_sw_credentials(redirect_if_missing='html.index')
def call_page():
    return render_template('call.html') 
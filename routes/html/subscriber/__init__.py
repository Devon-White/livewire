from routes.html import html_bp
from flask import render_template, session, redirect, url_for
from stores.user_store import get_user_store
from utils.auth_decorators import require_sw_credentials, require_subscriber_login



@html_bp.route('/subscriber')
@require_sw_credentials(redirect_if_missing='html.index')
@require_subscriber_login(redirect_if_missing='html.login')
def subscriber_page():
    email = session['user_email']
    user = get_user_store().get(email, {})
    display_name = user.get('display_name') or ((user.get('first_name', '') + ' ' + user.get('last_name', '')).strip())
    return render_template('subscriber.html', display_name=display_name) 
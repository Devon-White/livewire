from routes.html import html_bp
from flask import redirect, url_for, session
from stores.active_subscribers_store import set_inactive_subscriber
from utils.session_utils import get_session_vars
from stores.user_store import get_user_store

@html_bp.route('/logout')
def logout():
    # Try to mark the current subscriber as inactive
    vars = get_session_vars()
    email = vars.get('user_email')
    subscriber_id = None
    if email:
        user = get_user_store().get(email)
        if user:
            subscriber_id = user.get('subscriber_id')
    if subscriber_id:
        set_inactive_subscriber(subscriber_id, session)
    session.clear()
    return redirect(url_for('html.login')) 
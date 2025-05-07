from routes.html import html_bp
from flask import render_template, session, redirect, url_for

@html_bp.route('/subscriber')
def subscriber_page():
    if not session.get('user_email'):
        return redirect(url_for('html.login'))
    from routes.html.signup import user_store
    email = session['user_email']
    user = user_store.get(email, {})
    display_name = user.get('display_name') or ((user.get('first_name', '') + ' ' + user.get('last_name', '')).strip())
    return render_template('subscriber.html', display_name=display_name) 
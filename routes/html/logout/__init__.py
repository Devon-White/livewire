from routes.html import html_bp
from flask import redirect, url_for, session

@html_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('html.login')) 
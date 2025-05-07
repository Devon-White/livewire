from routes.html import html_bp
from flask import render_template

@html_bp.route('/')
def index():
    return render_template('index.html') 
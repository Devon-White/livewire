from functools import wraps
from flask import session, redirect, url_for, flash


def require_sw_credentials(redirect_if_missing):
    """
    Decorator to ensure SignalWire credentials have been provided and validated in the session.
    Redirects to the specified endpoint if not set.
    :param redirect_if_missing: Flask endpoint name to redirect to if credentials are missing (e.g., 'html.index')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('sw_credentials_ok'):
                flash("Please provide your SignalWire credentials first.")
                return redirect(url_for(redirect_if_missing))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_subscriber_login(redirect_if_missing):
    """
    Decorator to ensure the user has signed in as a subscriber.
    Redirects to the specified endpoint if not set.
    :param redirect_if_missing: Flask endpoint name to redirect to if subscriber login is missing (e.g., 'html.login')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('subscriber_ok'):
                flash("Please sign in as a subscriber first.")
                return redirect(url_for(redirect_if_missing))
            return f(*args, **kwargs)
        return decorated_function
    return decorator 
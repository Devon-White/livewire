from flask import session as flask_session

def get_session_vars(session_obj=None):
    """
    Returns a dict of all relevant session variables for namespacing data.
    If session_obj is provided, use it instead of flask.session.
    """
    s = session_obj if session_obj is not None else flask_session
    return {
        'project_id': s.get('sw_project_id'),
        'auth_token': s.get('sw_auth_token'),
        'space_name': s.get('sw_space_name'),
        'swml_id': s.get('swml_id'),
        'user_email': s.get('user_email'),
    } 
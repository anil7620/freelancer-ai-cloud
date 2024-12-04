from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def annotation_function(*args, **kwargs):
        if not any(key in session for key in ['freelancer_id', 'admin_id', 'jobposter_id']):
            return redirect(url_for('admin_login'))  
        return f(*args, **kwargs)
    return annotation_function
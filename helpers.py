from functools import wraps
from flask import redirect, session, flash


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if session.get("user_id") is None:
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            flash("You are not authorized to access this page.", "danger")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function
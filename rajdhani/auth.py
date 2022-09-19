from flask import session


def login(email):
    session["user_email"] = email


def logout():
    session.pop("user_email")


def get_logged_in_user_email():
    return session.get("user_email")

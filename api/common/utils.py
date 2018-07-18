from flask import Response, session, render_template


def auth(func):
    def inner_auth(*args, **kwargs):
        if not session.get("username"):
            return Response(render_template("login.html"), mimetype='text/html')
        else:
            return func(*args, **kwargs)
    return inner_auth


def error_response(redirect_url, message):
    return Response(render_template("error.html", message=str(message), redirect_url=redirect_url ),
                    mimetype='text/html', status=400)

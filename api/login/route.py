from flask_restful import Resource
from flask import request, session
from api.login.actions import AccessActions
from api.common.definitions import CommonDefinitions
from api.common.utils import error_response


class Access(Resource):
    def __init__(self):
        self.access = AccessActions()
        self.definitions = CommonDefinitions()

    def get(self, action=None):
        url = ""
        try:
            action_name = request.args.get("action")
            if action and action == "logout":
                response = self.access.logout()
            elif action and action == "login" and action_name == "redirect":
                username = session.get("username")
                password = session.get("password")
                response = self.access.login(username, password)
            elif action and action == "profile":
                name = session.get("username")
                url = "http://localhost:5000/login?action=redirect"
                response = self.access.profile_data(name)
            else:
                response = self.access.index()
            return response
        except Exception as e:
            if url:
                return error_response(url, str(e.message))
            return error_response("http://localhost:5000/", str(e.message))

    def post(self, action=None):
        username = request.form["username"]
        password = request.form["password"]
        try:
            if action and action == "login":
                response = self.access.login(username, password)
                return response
            else:
                raise Exception("URL not found")
        except Exception as e:
            return error_response("http://localhost:5000/", str(e.message))

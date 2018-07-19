from datetime import datetime
from datetime import timedelta
from collections import OrderedDict
from flask import render_template, Response, session

from db.db_conn import UserApi
from db.db_conn import StockHistoryApi


class AccessActions(object):
    def __init__(self):
        self.user_api = UserApi()
        self.stock_history = StockHistoryApi()

    def to_dict(self, stock_history):
        stock_history_dict = OrderedDict([("Order_Id", stock_history.id),
                                          ("Ticker_Symbol", stock_history.symbol),
                                          ("Quantity", stock_history.quantity),
                                          ("Status", "Bought" if stock_history.buy_flag else "Sold")])
        return stock_history_dict

    def profile_to_dict(self, user_data):
        profile_dict = OrderedDict([("UserID", user_data.id),
                                    ("Username", user_data.username),
                                    ("Funds Available", user_data.balance_amount),
                                    ("Role", user_data.role)])
        return profile_dict

    def login_data(self, data, username, user_id):
        stock_history_obj = self.stock_history.get_histories(dict(user_id=data.id))
        stock_history_list = list()
        for stock_history in stock_history_obj:
            stock_history_list.append(self.to_dict(stock_history))
        response = Response(render_template("stock_history.html", name=username, stock_history=stock_history_list,
                                            user_id=user_id), mimetype='text/html')
        return response

    def profile_data(self, name):
        try:
            user_data = self.user_api.get_user(dict(username=name))
            if not user_data:
                raise Exception("Invalid User")
            if user_data.role == "admin":
                user_data = self.user_api.get_users()
            else:
                user_data = [user_data]
            profile_data = list()
            for data in user_data:
                profile_data.append(self.profile_to_dict(data))
            response = Response(render_template("profile_data.html", profile_data=profile_data, name=name),
                                mimetype='text/html')
            return response
        except Exception as e:
            raise Exception(e)

    def login(self, username, password):
        try:
            if not (username or password):
                raise Exception("Username/Password is mandatory")
            data = self.user_api.get_user(dict(username=username, password=password))
            if data:
                session["username"] = username
                session["password"] = password
                session["user_id"] = data.id
                update_dict = dict(expiry_time=datetime.utcnow() + timedelta(hours=1))
                self.user_api.update(update_dict, dict(username=username, password=password))
                return self.login_data(data, username, user_id=data.id)
            else:
                raise Exception("Invalid Username/Password")
        except Exception as e:
            raise Exception(e)

    def logout(self):
        try:
            session.clear()
            return self.index()
        except Exception as e:
            raise Exception(e)

    def index(self):
        return Response(render_template("login.html"), mimetype='text/html')

from alpha_vantage.timeseries import TimeSeries
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from flask import session, render_template, Response, redirect

from api.login.actions import AccessActions
from db.db_conn import StockAggregateApi
from db.db_conn import StockHistoryApi
from db.db_conn import UserApi
from db.db_conn import redis_db


class StockActions(object):
    def __init__(self):
        self.user_api = UserApi()
        self.stock_history = StockHistoryApi()
        self.access = AccessActions()
        self.stock_aggregate_api = StockAggregateApi()
        self.redis_conn = redis_db()

    def view_stock(self, symbol, internal=False):
        try:
            if not symbol:
                raise Exception("Symbol is mandatory and it cannot be empty")
            symbol = symbol.upper()
            stock_quote = self.redis_conn.hgetall(symbol)
            if not stock_quote:
                ts = TimeSeries(key="check")
                stock_data, info = ts.get_intraday(symbol=symbol, interval="60min", outputsize="compact")
                latest_time = str(datetime.utcnow() - timedelta(days=3))
                for k, v in stock_data.items():
                    if k > latest_time:
                        latest_time = k
                req_data = stock_data[latest_time]
                high = req_data["2. high"]
                low = req_data["3. low"]
                average_cost = (float(high) + float(low))/2
                stock_quote = OrderedDict([("symbol", symbol), ("price", average_cost),
                                           ("volume", req_data["5. volume"]), ("timestamp", latest_time)])
                self.redis_conn.hmset(symbol, stock_quote)
            if internal:
                return stock_quote
            return Response(render_template("stock_quote.html", stock_quote=stock_quote, name=session["username"],
                                            user_id=session["user_id"]), mimetype='text/html')
            # return stock_quote
        except Exception as e:
            raise Exception(e)

    def stock_aggregate(self, buy_flag, symbol, user_id, quantity):
        try:
            aggregate = self.stock_aggregate_api.get_aggregate(dict(user_id=user_id))
            if buy_flag:
                if not aggregate:
                    stock_data = [dict(symbol=symbol, quantity=quantity)]
                    data_dict = dict(user_id=user_id, stock_data=stock_data)
                    self.stock_aggregate_api.create(data_dict)
                else:
                    stock_data = aggregate.stock_data
                    stock_available = False
                    for index, data in enumerate(stock_data):
                        if data.get("symbol") == symbol:
                            stock_data[index]["quantity"] += int(quantity)
                            stock_available = True
                    if not stock_available:
                        data = dict(symbol=symbol, quantity=quantity)
                        stock_data.append(data)
                    self.stock_aggregate_api.update(dict(stock_data=stock_data), dict(user_id=user_id))
            else:
                if not aggregate:
                    raise Exception("You have no stocks to sell")
                else:
                    stock_data = aggregate.stock_data
                    stock_available = False
                    for index, data in enumerate(stock_data):
                        if data.get("symbol") == symbol and stock_data[index]["quantity"] >= int(quantity):
                            stock_data[index]["quantity"] -= int(quantity)
                            stock_available = True
                    if not stock_available:
                        raise Exception("The requested stocks are not available to sell")
                    self.stock_aggregate_api.update(dict(stock_data=stock_data), dict(user_id=user_id))
        except Exception as e:
            raise Exception(e)

    def updated_user_balance(self, buy_flag, symbol, user_id, quantity):
        try:
            if not float(quantity):
                raise Exception("Provide a valid quantity")
            view_stock = self.view_stock(symbol=symbol, internal=True)
            user_details = self.user_api.get_user(dict(id=user_id))
            if not user_details:
                raise Exception("User not found")
            consumed_amount = float(quantity) * float(view_stock["price"])
            if buy_flag:
                user_updated_balance = user_details.balance_amount - consumed_amount
                if user_updated_balance < 0:
                    raise Exception("Not enough funds available in your account")
            else:
                user_updated_balance = user_details.balance_amount + consumed_amount
            self.user_api.update(dict(balance_amount=user_updated_balance), dict(id=user_id))
            self.stock_aggregate(buy_flag=buy_flag, symbol=symbol, user_id=user_id, quantity=quantity)
            self.stock_history.create(dict(user_id=user_id, symbol=symbol, quantity=quantity, buy_flag=buy_flag))
        except Exception as e:
            raise Exception(e)

    def buy_sell_stock(self, symbol, quantity, user_id, buy_flag):
        try:
            if buy_flag == "1":
                buy_flag = True
            else:
                buy_flag = False
            self.updated_user_balance(buy_flag, symbol, user_id, quantity)
            return redirect("http://localhost:5000/login?action=redirect")
        except Exception as e:
            raise Exception(e)

    def fetch_stock_aggregate(self, stock_user_id):
        try:
            user_id = session.get("user_id")
            user_data = self.user_api.get_user(dict(id=user_id))
            if stock_user_id != user_id and user_data.role != "admin":
                raise Exception("Permission denied")
            stock_aggregate_data = self.stock_aggregate_api.get_aggregate(dict(user_id=stock_user_id))
            if not stock_aggregate_data:
                raise Exception("No stocks available for the user")
            stock_data = stock_aggregate_data.stock_data
            response = Response(render_template("stock_aggregate.html", name=session.get("username"),
                                                stock_aggregate=stock_data), mimetype='text/html')
            return response
        except Exception as e:
            raise Exception(e)

from flask_restful import Resource
from flask import request

from api.stock.actions import StockActions
from api.common.utils import auth, error_response
from api.common.definitions import CommonDefinitions


class Stock(Resource):
    def __init__(self):
        self.stockactions = StockActions()
        self.definitions = CommonDefinitions()

    @auth
    def get(self, action=None):
        try:
            self.definitions.url = "login?action=redirect"
            symbol = request.args.get("symbol")
            stock_user_id = request.args.get("stock_user_id")
            if action and action == "view":
                if not symbol:
                    raise Exception("Symbol is mandatory")
                return self.stockactions.view_stock(symbol)
            elif action and action == "stock_aggregate":
                self.definitions.url = "profile"
                if not stock_user_id:
                    raise Exception("Stock user id is mandatory")
                return self.stockactions.fetch_stock_aggregate(int(stock_user_id))
            else:
                raise Exception("URL Not found")
        except Exception as e:
            return error_response("http://localhost:5000/%s" % self.definitions.url, str(e.message))

    @auth
    def post(self, action=None):
        try:
            self.definitions.url = "login?action=redirect"
            symbol = str(request.form.get("symbol"))
            if not symbol:
                raise Exception("Symbol is mandatory")
            quantity = int(request.form.get("quantity"))
            user_id = int(request.form.get("id"))
            buy_flag = request.form.get("buy_flag")
            if action == "buy":
                symbol = symbol.upper()
                return self.stockactions.buy_sell_stock(symbol, quantity, user_id, buy_flag)
            else:
                raise Exception("Url Not found")
        except Exception as e:
            return error_response("http://localhost:5000/%s" % self.definitions.url, str(e.message))

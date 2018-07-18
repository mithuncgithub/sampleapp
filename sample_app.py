from flask import Flask
from flask_restful import Api
from api.login.route import Access
from api.stock.route import Stock

app = Flask(__name__)
app.secret_key = 'abcdef'
api = Api(app)

api.add_resource(Access, "/<action>", "/")

api.add_resource(Stock, "/stock/<action>")

if __name__ == '__main__':
    app.run(debug=False)

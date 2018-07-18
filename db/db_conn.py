import redis
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
from sqlalchemy.orm.attributes import flag_modified

from db.models import User
from db.models import StockHistory
from db.models import StockAggregate


#  dialect+driver(optional: will take default as psycopg2)://user:password@host:port/db_name
def connect_db(database_name="stock_db"):
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/%s' % database_name)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    return session, engine


def redis_db():
    conn = redis.Redis(host="localhost", port=6379)
    return conn


class UserApi(object):
    def __init__(self):
        self.session, self.engine = connect_db()
        User.__table__.create(self.engine, checkfirst=True)

    def get_users(self, query=None):
        users = self.session.query(User)
        if query:
            for key, value in query.items():
                users = users.filter(getattr(User, key) == value)
        result = users.all()
        return result

    def get_user(self, query):
        users = self.session.query(User)
        if query:
            for key, value in query.items():
                users = users.filter(getattr(User, key) == value)
        result = users.first()
        return result

    def create(self, user_dict):
        largest_id = self.session.query(func.max(User.id)).scalar()
        if not largest_id:
            largest_id = 0
        user = User(username=user_dict.get("username"),
                    id=largest_id+1,
                    password=user_dict.get("password"),
                    expiry_time=datetime.utcnow(),
                    balance_amount=10000)
        self.session.add(user)
        self.session.commit()
        return True

    def update(self, update_dict, query):
        users = self.session.query(User)
        if query:
            for key, value in query.items():
                users = users.filter(getattr(User, key) == value)
        user = users.first()
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        self.session.commit()
        return True

    def delete(self, query):
        users = self.session.query(User)
        if query:
            for key, value in query.items():
                users = users.filter(getattr(User, key) == value)
        user = users.first()
        self.session.delete(user)
        self.session.commit()
        return True


class StockHistoryApi(object):
    def __init__(self):
        self.session, self.engine = connect_db()
        StockHistory.__table__.create(self.engine, checkfirst=True)

    def get_histories(self, query=None):
        stock_history = self.session.query(StockHistory)
        if query:
            for key, value in query.items():
                stock_history = stock_history.filter(getattr(StockHistory, key) == value)
        result = stock_history.all()
        return result

    def get_history(self, query=None):
        stock_history = self.session.query(StockHistory)
        if query:
            for key, value in query.items():
                stock_history = stock_history.filter(getattr(StockHistory, key) == value)
        result = stock_history.first()
        return result

    def create(self, data_dict):
        largest_id = self.session.query(func.max(StockHistory.id)).scalar()
        if not largest_id:
            largest_id = 0
        stock_history = StockHistory(user_id=data_dict.get("user_id"),
                                     symbol=data_dict.get("symbol"),
                                     quantity=data_dict.get("quantity"),
                                     buy_flag=data_dict.get("buy_flag"),
                                     id=largest_id+1)
        self.session.add(stock_history)
        self.session.commit()
        return True

    def update(self, data_dict, query):
        stock_history = self.session.query(StockHistory)
        if query:
            for key, value in query.items():
                stock_history = stock_history.filter(getattr(StockHistory, key) == value)
        stock_history = stock_history.first()
        for key, value in data_dict.items():
            setattr(stock_history, key, value)
        self.session.add(stock_history)
        self.session.commit()
        return True


class StockAggregateApi(object):
    def __init__(self):
        self.session, self.engine = connect_db()
        StockAggregate.__table__.create(self.engine, checkfirst=True)

    def get_aggregates(self, query=None):
        stock_aggregate = self.session.query(StockAggregate)
        if query:
            for key, value in query.items():
                stock_aggregate = stock_aggregate.filter(getattr(StockAggregate, key) == value)
        result = stock_aggregate.all()
        return result

    def get_aggregate(self, query=None):
        stock_aggregate = self.session.query(StockAggregate)
        if query:
            for key, value in query.items():
                stock_aggregate = stock_aggregate.filter(getattr(StockAggregate, key) == value)
        result = stock_aggregate.first()
        return result

    def create(self, data_dict):
        largest_id = self.session.query(func.max(StockAggregate.id)).scalar()
        if not largest_id:
            largest_id = 0
        stock_aggregate = StockAggregate(id=largest_id+1,
                                         user_id=data_dict.get("user_id"),
                                         stock_data=data_dict.get("stock_data"))
        self.session.add(stock_aggregate)
        self.session.commit()
        return True

    def update(self, data_dict, query):
        stock_aggregate = self.session.query(StockAggregate)
        if query:
            for key, value in query.items():
                stock_aggregate = stock_aggregate.filter(getattr(StockAggregate, key) == value)
        stock_aggregate = stock_aggregate.first()
        for key, value in data_dict.items():
            setattr(stock_aggregate, key, value)
        if "stock_data" in data_dict:
            flag_modified(stock_aggregate, "stock_data")
        self.session.add(stock_aggregate)
        self.session.commit()
        return True

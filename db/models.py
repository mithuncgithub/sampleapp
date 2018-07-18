from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()


class User(base):
    __tablename__ = 'user'
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True)
    expiry_time = Column(DateTime, nullable=False)
    role = Column(String, server_default="member")
    balance_amount = Column(Float, nullable=False)


class StockHistory(base):
    __tablename__ = 'stock_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    buy_flag = Column(Boolean, nullable=False)


class StockAggregate(base):
    __tablename__ = 'stock_aggregate'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    stock_data = Column(JSON)

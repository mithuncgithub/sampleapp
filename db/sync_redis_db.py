import redis
from alpha_vantage.timeseries import TimeSeries
from datetime import datetime, timedelta
from collections import OrderedDict
import time

conn = redis.Redis(host="localhost", port=6379)

keys = conn.keys()
for key in keys:
    print(key)
    ts = TimeSeries(key="check")
    try:
        stock_data, info = ts.get_intraday(symbol=key, interval="60min", outputsize="compact")
        print("Updated for %s" % key)
        time.sleep(15)
    except:
        print("Failed for %s" % key)
        continue
    latest_time = str(datetime.utcnow() - timedelta(days=3))
    for k, v in stock_data.items():
        if k > latest_time:
            latest_time = k
    req_data = stock_data[latest_time]
    high = req_data["2. high"]
    low = req_data["3. low"]
    average_cost = (float(high) + float(low)) / 2
    stock_quote = OrderedDict([("symbol", key), ("price", average_cost),
                               ("volume", req_data["5. volume"]), ("timestamp", latest_time)])
    conn.hmset(key, stock_quote)

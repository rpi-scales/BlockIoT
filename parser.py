import requests
import time
import datetime
import ciso8601

def ripplehealth(url):
    r = requests.get(url)
    result = r.json()
    data = dict()
    rtime = 0
    for element in result['data']['records']:
        ts = ciso8601.parse_datetime(element)
        rtime = int(time.mktime(ts.timetuple())) - int(time.mktime(ts.timetuple())) % 86400
        if (str(rtime) in data):
            data[str(rtime)] = str(int(data[str(rtime)]) + 1)
        else:
            data[str(rtime)] = str(1)
    return data
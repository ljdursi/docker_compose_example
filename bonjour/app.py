import time
import logging
import logstash

import redis
from flask import Flask


# set up logging
_LOGHOST = "logstash"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logstash.LogstashHandler(_LOGHOST, 5959, version=1))

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)


def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.route('/')
def bonjour():
    count = get_hit_count()
    return "Bonjour, le monde!  J'ai été vu {} fois.\n".format(count)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

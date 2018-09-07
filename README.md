# Docker compose example

This is a simple multi-service docker compose example with nginx
as a reverse proxy, two essentially equivalent simple Flask services
each connecting to a Redis backend, all logging to logstash.

It borrows heavily from the [Getting Started with Docker
Compose](https://docs.docker.com/compose/gettingstarted) and
https://rzetterberg.github.io/nginx-elk-logging.html for the nginx
-> logstash logging.

To get this up and running, make sure [docker compose is installed](https://docs.docker.com/compose/install/),
and run:

```bash
docker-compose build
docker-compose up -d
```

From there, you should be able to access the two endpoints

```bash
curl -L  http://0.0.0.0/bonjour
curl -L  http://0.0.0.0/hello
```

and you can shut down the multi-service web app with

```bash
docker-compose down
```

Logs are output (as JSON lines) in logs/log.out. 

The [nginx config](api_gw/nginx.conf) proxies 
between the hello and bonjour servies:

```
server {
    listen 80;

    location /hello {
        proxy_pass http://hello_en;
        rewrite ^/hello(.*)$ /$1 break;
    }

    location /bonjour {
        proxy_pass http://hello_fr;
        rewrite ^/bonjour(.*)$ /$1 break;
    }
}
```

loadbalancing across 2 instances of the hello service and 1 of the bonjour service:

```
upstream hello_en {
    least_conn;
    server hello1:5000 weight=10 max_fails=3 fail_timeout=30s;
    server hello2:5000 weight=10 max_fails=3 fail_timeout=30s;
}

upstream hello_fr {
    least_conn;
    server bonjour:5000 weight=10 max_fails=3 fail_timeout=30s;
}
```

Those services read and increment a counter from redis.

```python
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
```

All orchestration is done through the [docker compose file](docker-compose.yml)

```yaml
version: '3'
services:

  api_gw:
    build: ./api_gw
    restart: always
    ports:
     - "80:80"
    links:
     - hello1
     - hello2
     - bonjour
     - logstash

  hello1:
    build: ./hello
    ports:
     - "5001:5000"
    links:
     - redis

  hello2:
    build: ./hello
    ports:
     - "5002:5000"
    links:
     - redis

  bonjour:
    build: ./bonjour
    ports:
     - "5100:5000"
    links:
     - redis

  redis:
    image: "redis:alpine"

  logstash:
    build: ./logstash
    ports:
     - "5140:5140"
     - "9200:9200"
    volumes:
     - ./logs:/logs
     - ./logs/logstash:/var/log
```

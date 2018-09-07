FROM logstash:latest

ENV PLUGIN_BIN "/usr/share/logstash/bin/logstash-plugin"

RUN "$PLUGIN_BIN" install logstash-input-syslog
RUN "$PLUGIN_BIN" install logstash-filter-date
RUN "$PLUGIN_BIN" install logstash-filter-grok
RUN "$PLUGIN_BIN" install logstash-filter-useragent

COPY ./conf /etc/logstash

EXPOSE 9200
EXPOSE 5140

CMD ["-f", "/etc/logstash/logstash.conf"]

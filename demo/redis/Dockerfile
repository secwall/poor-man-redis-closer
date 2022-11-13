FROM ubuntu:jammy

RUN apt update && apt -y install curl gpg lsb-release
RUN curl -fsSL https://packages.redis.io/gpg | gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" > /etc/apt/sources.list.d/redis.list
RUN apt update && apt -y install redis redis-sentinel iptables supervisor python3-venv && mkdir /opt/closer
COPY ./src /opt/closer/src
COPY ./setup.py /opt/closer/setup.py
RUN python3 -m venv /opt/closer/venv && /opt/closer/venv/bin/pip install /opt/closer
COPY ./demo/redis/supervisor.conf /etc/supervisor/conf.d/demo.conf
COPY ./demo/redis/redis.conf /etc/redis/redis.conf
COPY ./demo/redis/sentinel.conf /etc/redis/sentinel.conf
COPY ./demo/redis/closer.yaml /etc/redis-closer.yaml
COPY ./demo/redis/init.py /opt/closer/init.py
RUN chmod +x /opt/closer/init.py
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]

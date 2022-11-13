FROM ubuntu:jammy

RUN apt update && apt -y install python3-venv && mkdir /opt/runner
RUN python3 -m venv /opt/runner/venv && /opt/runner/venv/bin/pip install docker==6.0.1 redis==4.3.4
COPY ./demo/runner/run.py /opt/runner/run.py
CMD ["/bin/sleep", "infinity"]

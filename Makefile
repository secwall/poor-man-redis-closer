.PHONY: demo clean prepare run-with-closer run-without-closer stop demo-with-closer demo-without-closer

demo-with-closer: prepare run-with-closer stop

demo-without-closer: prepare run-without-closer stop

prepare: venv/bin/docker-compose
	./venv/bin/docker-compose build
	./venv/bin/docker-compose -p poor-man-redis-closer up -d >compose.log 2>&1

run-with-closer: prepare
	./venv/bin/docker-compose exec runner /opt/runner/venv/bin/python /opt/runner/run.py

run-without-closer: prepare
	./venv/bin/docker-compose exec runner /opt/runner/venv/bin/python /opt/runner/run.py --no-closer

stop:
	./venv/bin/docker-compose down

venv:
	python3 -m venv venv

venv/bin/docker-compose: venv
	./venv/bin/pip install docker-compose==1.29.2 redis==4.3.4

clean:
	rm -rf compose.log venv

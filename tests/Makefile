
test: .env/bin/seleniumbase wait
	.env/bin/pytest tests_selenium.py --server=127.0.0.1 --port=4444 --headed

ci: wait
	pytest tests_selenium.py --server=127.0.0.1 --port=4444

wait:
	while ! ./test_haproxy.sh ; do sleep 1; done

selenium:
	podman run \
		-p 4444:4444 \
		-p 7900:7900 \
		--shm-size="2g" \
		-v ${PWD}/assets:/assets \
		docker.io/selenium/standalone-chrome:latest

.env:
	virtualenv .env

.env/bin/seleniumbase: .env
	.env/bin/pip install -r requirements.txt

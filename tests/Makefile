
test: .env/bin/seleniumbase
	.env/bin/pytest tests_selenium.py --server=127.0.0.1 --port=4444 --headed

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

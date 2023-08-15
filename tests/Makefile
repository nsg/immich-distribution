test: .env/bin/seleniumbase external-test-files wait
	.env/bin/pytest tests_selenium.py --server=127.0.0.1 --port=4444 --headed --html=report.html

trace: .env/bin/seleniumbase external-test-files wait
	.env/bin/pytest tests_selenium.py --server=127.0.0.1 --port=4444 --headed --html=report.html --trace

ci: external-test-files wait
	pytest tests_selenium.py --server=127.0.0.1 --port=4444 --html=report.html

external-test-files:
	mkdir -p external-test-files

	cd external-test-files && for file in $(shell cat external-test-files.list); do \
		wget $$file; \
	done

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

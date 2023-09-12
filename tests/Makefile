test: .env/bin/seleniumbase prepare-test-file wait check-selenium
	.env/bin/pytest tests_selenium.py --server=127.0.0.1 --port=4444 --headed --html=report.html

trace: .env/bin/seleniumbase prepare-test-file wait
	.env/bin/pytest tests_selenium.py --server=127.0.0.1 --port=4444 --headed --html=report.html --trace

ci: prepare-test-file wait
	pytest tests_selenium.py --server=127.0.0.1 --port=4444 --html=report.html

prepare-test-file: external-test-files
	mkdir -p ${HOME}/snap/immich-distribution/current/tests
	mkdir -p ${HOME}/snap/immich-distribution/current/tests_external
	cp -r assets ${HOME}/snap/immich-distribution/current/tests
	cp -r external-test-files ${HOME}/snap/immich-distribution/current/tests_external

external-test-files:
	mkdir -p external-test-files

	cd external-test-files && for file in $(shell cat external-test-files.list); do \
		wget $$file; \
	done

wait:
	./test_haproxy.sh

check-selenium:
	nc -v -w1 127.0.0.1 4444 || (echo "Selenium is not running"; exit 1)

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

test: .env/bin/seleniumbase prepare-test-file wait check-selenium
	.env/bin/pytest tests_selenium.py --server=127.0.0.1 --port=4444 --headed --html=report.html

trace: .env/bin/seleniumbase prepare-test-file wait
	.env/bin/pytest tests_selenium.py --server=127.0.0.1 --port=4444 --headed --html=report.html --trace

ci: prepare-test-file wait
	pytest tests_selenium.py --server=127.0.0.1 --port=4444 --html=report.html

prepare-test-file: external-test-files update-snap-symlinks-for-user
	mkdir -p ${HOME}/snap/immich-distribution/current/tests
	mkdir -p ${HOME}/snap/immich-distribution/current/tests_external
	for asset in assets/*; do \
		echo $$asset | grep -q py__ \
			|| cp $$asset ${HOME}/snap/immich-distribution/current/tests/; \
	done
	cp -r external-test-files ${HOME}/snap/immich-distribution/current/tests_external

external-test-files: update-snap-symlinks-for-user
	mkdir -p external-test-files

	cd external-test-files && for file in $(shell cat external-test-files.list); do \
		wget -c $$file; \
	done

update-snap-symlinks-for-user:
	immich-distribution.cli -h > /dev/null 2>&1

wait:
	./test_haproxy.sh

check-selenium:
	nc -v -w1 127.0.0.1 4444 || (echo "Selenium is not running"; exit 1)

selenium:
	podman run \
		-p 4444:4444 \
		-p 7900:7900 \
		--shm-size="2g" \
		docker.io/selenium/standalone-chrome:latest

.env:
	virtualenv .env

.env/bin/seleniumbase: .env
	.env/bin/pip install -r requirements.txt

#
# This Makefile is used to run tests for Immich Distribution.
# The tests are written in Python and use the SeleniumBase framework.
#

PYTEST = .env/bin/pytest
PYTHON = .env/bin/python

ifndef CI
    PYTEST_EXTRA_ARGS = --headed
    PYTEST_LOCALTEST_DEPENDENCIES = .env/bin/seleniumbase check-selenium
else
    PYTEST_EXTRA_ARGS =
    PYTEST_LOCALTEST_DEPENDENCIES =
endif

test: test-prep
	make test-assets

test-prep: ${PYTEST} ${PYTEST_LOCALTEST_DEPENDENCIES} wait
	${PYTEST} tests_prep.py --server=127.0.0.1 --port=4444 ${PYTEST_EXTRA_ARGS} --dashboard --html=report/index.html

test-selenium: ${PYTEST} ${PYTEST_LOCALTEST_DEPENDENCIES} test-assets wait
	${PYTEST} tests_selenium.py --server=127.0.0.1 --port=4444 ${PYTEST_EXTRA_ARGS} --dashboard --html=report/index.html

test-sync: ${PYTEST} test-assets wait
	SERVICE_STATE=default ${PYTEST} tests_sync_service.py
	sudo snap set immich-distribution sync-enabled=true
	sleep 10
	SERVICE_STATE=enabled ${PYTEST} tests_sync_service.py
	sudo snap set immich-distribution sync="$(shell cat secret.txt)"
	sleep 10
	sudo chmod -R 777 /var/snap/immich-distribution/common/sync
	SERVICE_STATE=running ${PYTEST} tests_sync_service.py
	sudo snap set immich-distribution sync-delete-threshold=0
	sleep 10
	SERVICE_STATE=threshold ${PYTEST} tests_sync_service.py

test_prep_%: .env/bin/seleniumbase test-assets
	${PYTEST} tests_prep.py --server=127.0.0.1 --port=4444 --headed -k $* --html=report/index.html

test_selenium_%: .env/bin/seleniumbase test-assets
	${PYTEST} tests_selenium.py --server=127.0.0.1 --port=4444 --headed -k $* --html=report/index.html

test-assets:
	git clone https://github.com/immich-app/test-assets.git
	cd test-assets && git checkout 61131e84ec91d316265aebe375b3155308baaa89

cleantest:
	make -C .. remove install tests

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

movie:
	${PYTHON} movie.py

.env:
	python3 -m venv .env

${PYTEST}: .env
	.env/bin/pip install -r requirements.txt

.env/bin/seleniumbase: .env
	.env/bin/pip install -r requirements.txt

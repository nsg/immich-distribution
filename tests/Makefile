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
	make test-selenium

test-prep: ${PYTEST} ${PYTEST_LOCALTEST_DEPENDENCIES} wait
	${PYTEST} tests_prep.py --server=127.0.0.1 --port=4444 ${PYTEST_EXTRA_ARGS} --dashboard --html=report/index.html

test-selenium: ${PYTEST} ${PYTEST_LOCALTEST_DEPENDENCIES} test-assets wait
	${PYTEST} tests_selenium.py --server=127.0.0.1 --port=4444 ${PYTEST_EXTRA_ARGS} --dashboard --html=report/index.html

test-sync: test-assets wait
	./test_sync.sh

test-cli: wait
	./test_cli.sh

test_prep_%: ${PYTEST} ${PYTEST_LOCALTEST_DEPENDENCIES}
	${PYTEST} tests_prep.py --server=127.0.0.1 --port=4444 --headed -k $* --html=report/index.html

test_selenium_%: ${PYTEST} ${PYTEST_LOCALTEST_DEPENDENCIES} test-assets
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
	@echo "Starting Selenium with Chrome in a Podman container..."
	@echo "Access it via http://127.0.0.1:7900?autoconnect=true&password=secret"
	podman run \
		-p 4444:4444 \
		-p 0.0.0.0:7900:7900 \
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

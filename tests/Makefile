#
# This Makefile is used to run tests for Immich Distribution.
# The tests are written in Python and use Playwright for browser automation.
#

PYTEST = .env/bin/pytest
PYTHON = .env/bin/python

ifndef CI
    PYTEST_EXTRA_ARGS = --headed
    PYTEST_LOCALTEST_DEPENDENCIES =
else
    PYTEST_EXTRA_ARGS =
    PYTEST_LOCALTEST_DEPENDENCIES =
endif

test: test-validate test-prep
	make test-photos

test-validate:
	./test_vips_version.sh

test-prep: ${PYTEST} ${PYTEST_LOCALTEST_DEPENDENCIES} wait
	${PYTEST} tests_prep.py ${PYTEST_EXTRA_ARGS} --html=report/index.html

test-photos: ${PYTEST} ${PYTEST_LOCALTEST_DEPENDENCIES} test-assets wait
	${PYTEST} tests_assets.py ${PYTEST_EXTRA_ARGS} --html=report/index.html

test-sync: test-assets wait
	./test_sync.sh

test-cli: wait
	./test_cli.sh

test-backup: wait
	./test_backup.sh

test_prep_%: ${PYTEST} ${PYTEST_LOCALTEST_DEPENDENCIES}
	${PYTEST} tests_prep.py ${PYTEST_EXTRA_ARGS} -k $* --html=report/index.html

test_photos_%: ${PYTEST} ${PYTEST_LOCALTEST_DEPENDENCIES} test-assets
	${PYTEST} tests_assets.py ${PYTEST_EXTRA_ARGS} -k $* --html=report/index.html

test-assets:
	git clone https://github.com/immich-app/test-assets.git
	cd test-assets && git checkout 61131e84ec91d316265aebe375b3155308baaa89

cleantest:
	make -C .. remove install tests

wait:
	./test_haproxy.sh

.env:
	python3 -m venv .env

${PYTEST}: .env
	.env/bin/pip install -r requirements.txt
	.env/bin/playwright install chromium

#
# This Makefile is used to run tests for Immich Distribution.
# The tests are written in Python and use Playwright for browser automation.
#

PYTEST = uv run pytest

ifndef CI
    PYTEST_EXTRA_ARGS = -v -s --tb=short --headed -x
    PYTEST_LOCALTEST_DEPENDENCIES =
else
    # --timeout=580: 10 min per test, uses signal method (allows teardown/video save)
    PYTEST_EXTRA_ARGS = -v -s --tb=short --timeout=580 -x
    PYTEST_LOCALTEST_DEPENDENCIES =
endif

test: test-validate test-prep
	make test-photos

test-validate:
	./test_vips_version.sh

test-prep: .venv ${PYTEST_LOCALTEST_DEPENDENCIES} wait
	${PYTEST} tests_prep.py ${PYTEST_EXTRA_ARGS} --html=report/index.html

test-photos: .venv ${PYTEST_LOCALTEST_DEPENDENCIES} test-assets wait
	${PYTEST} tests_assets.py ${PYTEST_EXTRA_ARGS} --html=report/index.html

test-sync: test-assets wait
	./test_sync.sh

test-cli: wait
	./test_cli.sh

test-backup: wait
	./test_backup.sh

test_prep_%: .venv ${PYTEST_LOCALTEST_DEPENDENCIES}
	${PYTEST} tests_prep.py ${PYTEST_EXTRA_ARGS} -k $* --html=report/index.html

test_photos_%: .venv ${PYTEST_LOCALTEST_DEPENDENCIES} test-assets
	${PYTEST} tests_assets.py ${PYTEST_EXTRA_ARGS} -k $* --html=report/index.html

test-assets:
	git clone https://github.com/immich-app/test-assets.git
	cd test-assets && git checkout 61131e84ec91d316265aebe375b3155308baaa89

cleantest:
	make -C .. remove install tests

wait:
	./test_haproxy.sh

.venv: uv.lock
	uv sync
	uv run playwright install chromium

#
# This Makefile is used to run tests for Immich Distribution.
# The tests are written in Python and use the SeleniumBase framework.
#

test: .env/bin/seleniumbase test-assets wait check-selenium
	.env/bin/pytest tests_selenium.py --server=127.0.0.1 --port=4444 --headed --dashboard --html=report/index.html ${EXTRA_ARGS}

test-sync:
	SERVICE_STATE=default .env/bin/pytest tests_sync_service.py
	sudo snap set immich-distribution sync-enabled=true
	sleep 10
	SERVICE_STATE=enabled .env/bin/pytest tests_sync_service.py
	sudo snap set immich-distribution sync="$(shell cat secret.txt)"
	sleep 10
	sudo chmod -R 777 /var/snap/immich-distribution/common/sync
	SERVICE_STATE=running .env/bin/pytest tests_sync_service.py
	sudo snap set immich-distribution sync-delete-threshold=0
	sleep 10
	SERVICE_STATE=threshold .env/bin/pytest tests_sync_service.py

ci: test-assets wait
	pytest tests_selenium.py --server=127.0.0.1 --port=4444 --dashboard --html=report/index.html

ci-sync:
	SERVICE_STATE=default pytest tests_sync_service.py
	sudo snap set immich-distribution sync-enabled=true
	sleep 10
	SERVICE_STATE=enabled pytest tests_sync_service.py
	sudo snap set immich-distribution sync="$(shell cat secret.txt)"
	sleep 10
	sudo chmod -R 777 /var/snap/immich-distribution/common/sync
	SERVICE_STATE=running pytest tests_sync_service.py
	sudo snap set immich-distribution sync-delete-threshold=0
	sleep 10
	SERVICE_STATE=threshold pytest tests_sync_service.py

test_%: .env/bin/seleniumbase test-assets
	.env/bin/pytest tests_selenium.py --server=127.0.0.1 --port=4444 --headed -k $* --html=report/index.html

test-assets:
	git clone https://github.com/immich-app/test-assets.git
	cd test-assets && git checkout 61131e84ec91d316265aebe375b3155308baaa89

update-snap-symlinks-for-user:
	immich-distribution.backup -h 2>&1 | grep -q root

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

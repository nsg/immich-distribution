SNAP_FILE = $(shell ls -1t *.snap | head -1)

all: build install
	:

.PHONY: build
build:
	snapcraft --debug

.PHONY: install
install:
	sudo snap install --dangerous ${SNAP_FILE}

.PHONY: remove
remove:
	sudo snap remove --purge immich-distribution

testprod:
	cat ${SNAP_FILE} | ssh d -- lxc file push - immich-prod/root/${SNAP_FILE}
	ssh d lxc exec immich-prod -- snap install --dangerous /root/${SNAP_FILE}

shell:
	multipass shell snapcraft-immich-distribution

.PHONY: tests
tests:
	make -C tests test

.PHONY: selenium
selenium:
	make -C tests/ selenium

.PHONY: docs
docs:
	cd docs && poetry run mkdocs serve

clean:
	multipass purge
	snapcraft clean || true
	rm -rf SNAP_COMMON workdir temp tests/latest_logs/ *.snap

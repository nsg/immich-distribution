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

prodsnap: build
	cat ${SNAP_FILE} | ssh d -- lxc file push - immich-prod/root/${SNAP_FILE}
	ssh d lxc exec immich-prod -- snap install --dangerous /root/${SNAP_FILE}

prodstore:
	ssh d lxc exec immich-prod -- snap refresh --candidate --amend immich-distribution

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
	rm -rf SNAP_COMMON tests/latest_logs/ *.snap
	snapcraft clean

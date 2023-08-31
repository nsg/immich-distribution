SNAP_FILE = $(shell ls -1t *.snap | head -1)

all: build install
	:

.PHONY: build
build:
	snapcraft --debug

.PHONY: install
install:
	sudo snap install --dangerous ${SNAP_FILE}

beta: build
	cat ${SNAP_FILE} | ssh d -- lxc file push - immich-beta/root/${SNAP_FILE}
	ssh d lxc exec immich-beta -- snap install --dangerous /root/${SNAP_FILE}

beta2store:
	ssh d lxc exec immich-beta -- snap refresh --beta --amend immich-distribution

shell:
	multipass shell snapcraft-immich-distribution

.PHONY: docs
docs:
	cd docs && poetry run mkdocs serve

clean:
	rm -rf SNAP_COMMON tests/latest_logs/ *.snap
	snapcraft clean

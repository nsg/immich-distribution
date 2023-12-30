SNAP_FILE = $(shell ls -1t *.snap | head -1)
LXD_NAME = $(shell lxc list --project snapcraft snapcraft-immich-distribution -cn -f csv)

all: build install
	:

.PHONY: build
build:
	snapcraft

.PHONY: try
try:
	snapcraft try --debug --verbosity debug
	sudo snap try prime

.PHONY: shell
shell:
	lxc start --project snapcraft ${LXD_NAME} || :
	lxc shell --project snapcraft ${LXD_NAME}

.PHONY: install
install:
	sudo snap install --dangerous ${SNAP_FILE}

.PHONY: remove
remove:
	sudo snap remove --purge immich-distribution

testprod:
	cat ${SNAP_FILE} | ssh d -- lxc file push - immich-prod/root/${SNAP_FILE}
	ssh d lxc exec immich-prod -- snap install --dangerous /root/${SNAP_FILE}

.PHONY: tests
tests:
	make -C tests test

.PHONY: selenium
selenium:
	make -C tests/ selenium

.PHONY: docs
docs:
	cd docs && poetry run mkdocs serve

.PHONY: reset
reset: clean
	sudo snap remove immich-distribution
	sudo rm -rf prime

.PHONY: clean
clean:
	snapcraft clean || true
	rm -rf SNAP_COMMON tests/latest_logs/ *.snap

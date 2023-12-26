SNAP_FILE = $(shell ls -1t *.snap | head -1)

DEPENDENCIES = \
	dependencies/libvips \
	dependencies/node \
	dependencies/haproxy \
	dependencies/postgres \
	dependencies/typesense \
	dependencies/redis \
	dependencies/mimalloc \
	dependencies/ffmpeg \
	dependencies/python \
	dependencies/lego

DEPENDENCIES_SNAPS += $(addsuffix .snap, $(DEPENDENCIES))
DEPENDENCIES_NAMES := $(subst dependencies/,,$(DEPENDENCIES))

all: build install
	:

.PHONY: build
build: ${DEPENDENCIES_SNAPS}
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

beta: build
	cat ${SNAP_FILE} | ssh d -- lxc file push - immich-beta/root/${SNAP_FILE}
	ssh d lxc exec immich-beta -- snap install --dangerous /root/${SNAP_FILE}

beta2store:
	ssh d lxc exec immich-beta -- snap refresh --beta --amend immich-distribution

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

dependencies/%.snap: dependencies/%/snapcraft.yaml
	./dependency.py -b immich-distribution-$* -w workdir
	mv dependencies/$*/immich-distribution-$*.snap dependencies/$*.snap

workdir:
	for name in ${DEPENDENCIES_NAMES}; do \
		./dependency.py -b immich-distribution-$${name} -w workdir; \
		mv dependencies/$${name}/immich-distribution-$${name}.snap dependencies/$${name}.snap; \
	done

clean:
	for dependency in ${DEPENDENCIES_NAMES}; do \
		multipass delete snapcraft-immich-distribution-$$dependency || true; \
	done
	multipass purge
	snapcraft clean || true
	rm -rf SNAP_COMMON workdir temp tests/latest_logs/ *.snap
	rm -rf dependencies/*.snap

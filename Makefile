SNAP_FILE = $(shell ls -1t *.snap | head -1)
DEPENDENCIES = $(shell find dependencies -mindepth 1 -type d -print)
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
	@echo ">>> Building $*"
	cd dependencies/$* && snapcraft
	mv dependencies/$*/*.snap dependencies/$*.snap
	multipass stop snapcraft-immich-distribution-$* || true

	@echo ">>> Staging $*"
	mkdir -p temp
	mkdir -p workdir
	rm -rf temp/$*
	unsquashfs -d temp/$* dependencies/$*.snap
	rm -rf temp/$*/meta
	rm -rf temp/$*/snap
	for file in $$(cd temp/$*; find . -type f -print); do \
		if [ -f workdir/$$file ]; then \
			if [ "$$(sha256sum temp/$*/$$file | awk '{print $$1}')" != "$$(sha256sum workdir/$$file | awk '{print $$1}')" ]; then \
				echo "File $$file has different content in stage directory, aborting"; \
				exit 1; \
			fi; \
		fi; \
	done
	rsync -a temp/$*/* workdir
	rm -rf temp/$*

clean:
	for dependency in ${DEPENDENCIES_NAMES}; do \
		multipass delete snapcraft-immich-distribution-$$dependency || true; \
	done
	multipass purge
	snapcraft clean || true
	rm -rf SNAP_COMMON workdir temp tests/latest_logs/ *.snap
	rm -rf dependencies/*.snap

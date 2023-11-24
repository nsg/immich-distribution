SNAP_FILE = $(shell ls -1t *.snap | head -1)
DEPENDENCIES = $(shell find dependencies -mindepth 1 -type d -print)
DEPENDENCIES_SNAPS += $(addsuffix .snap, $(DEPENDENCIES))
WORKDIR_SNAPS := $(subst dependencies/,workdir/,$(DEPENDENCIES_SNAPS))

all: build install
	:

.PHONY: build
build: workdir
	snapcraft --debug

.PHONY: install
install:
	sudo snap install --dangerous ${SNAP_FILE}

.PHONY: remove
remove:
	sudo snap remove --purge immich-distribution

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

workdir:
	make ${WORKDIR_SNAPS}
	mv workdir/stage/* workdir
	rm -rf workdir/stage

dependencies/%.snap:
	cd dependencies/$* && snapcraft
	mv dependencies/$*/*.snap dependencies/$*.snap

workdir/%: dependencies/%
	mkdir -p workdir
	rm -rf workdir/$*
	unsquashfs -d workdir/$* $<
	rm -rf workdir/$*/meta
	rm -rf workdir/$*/snap
	mkdir -p workdir/stage
	for file in $$(cd workdir/$*; find . -type f -print); do \
		if [ -f workdir/stage/$$file ]; then \
			echo "File $$file already exists in stage directory, compare files hashes"; \
			if [ "$$(sha256sum workdir/$*/$$file | awk '{print $$1}')" != "$$(sha256sum workdir/stage/$$file | awk '{print $$1}')" ]; then \
				echo "File $file has different content in stage directory, aborting"; \
				exit 1; \
			fi; \
		fi; \
	done
	rsync -av workdir/$*/* workdir/stage/
	rm -rf workdir/$*

clean:
	rm -rf SNAP_COMMON tests/latest_logs/ *.snap
	snapcraft clean

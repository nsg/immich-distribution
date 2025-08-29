SNAP_FILE = $(shell ls -1t *.snap | head -1)
LXD_NAME = $(shell lxc list --project snapcraft snapcraft-immich-distribution -cn -f csv)

# Incus instance naming (override with INCUS_INSTANCE=foo INCUS_REMOTE=host)
INCUS_INSTANCE ?= idt
INCUS_REMOTE ?= local
INCUS_FULL_INSTANCE := $(INCUS_REMOTE):$(INCUS_INSTANCE)

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

#
# To run the tests:
#  - Make sure that the selenium container is running.
#  - Install the package locally (or inside the Incus VM).
#  - Run "make tests".
#

.PHONY: tests
tests:
	make -C tests test

.PHONY: cleantests
cleantests:
	sudo snap remove --purge immich-distribution
	make install
	make -C tests test

.PHONY: selenium
selenium:
	make -C tests/ selenium

#
# Run the documentation site locally with poetry.
#

.PHONY: docs
docs:
	cd docs && poetry run mkdocs serve

#
# Incus based build environment, can be used if you have Incus installed, and not
# the needed tooling to build snaps locally. This will create an Ubuntu 24.04 VM
# with the needed tooling and build the snap there. The current directory will be
# mounted into the VM at /build.
#
# Execute "make incus-setup" to setup the VM, "make incus-build" to build the snap
# and "make incus-destroy" to remove the VM.
#
# Prefix a make target with "incus-" to run it inside the VM.
#
# Variables controlling Incus targets:
#   INCUS_INSTANCE  (default: idt)
#   INCUS_REMOTE    (default: local)

.PHONY: incus-setup
incus-setup:
	incus init images:ubuntu/24.04 $(INCUS_FULL_INSTANCE) --vm -c limits.memory=6GiB -d root,size=30GiB
	incus config device add $(INCUS_FULL_INSTANCE) build disk source=${PWD} path=/build
	incus start $(INCUS_FULL_INSTANCE)
	sleep 30 # wait for the VM to boot
	incus exec $(INCUS_FULL_INSTANCE) -- sudo apt update
	incus exec $(INCUS_FULL_INSTANCE) -- sudo apt install snapd podman make python3.12-venv curl git jq -y
	sleep 10 # wait snapd to start
	incus exec $(INCUS_FULL_INSTANCE) -- sudo snap install --classic snapcraft
	incus exec $(INCUS_FULL_INSTANCE) -- sudo snap install lxd
	incus exec $(INCUS_FULL_INSTANCE) -- sudo lxd init --auto

incus-%:
	incus exec $(INCUS_FULL_INSTANCE) -- bash -c 'cd /build && make $*'

.PHONY: incus-install-artifact
incus-install-artifact:
	@echo "Installing the latest development snap package from ~/Downloads inside the Incus VM ..."
	@latest="$(shell ls -1t ~/Downloads/development-snap-package*.zip | head -1)"; \
	if [ -z "$$latest" ]; then \
		echo "No development snap package found in ~/Downloads"; \
		exit 1; \
	fi; \
	echo "Installing $$latest to $(INCUS_FULL_INSTANCE) ..."; \
	unzip -p "$$latest" | incus file push - $(INCUS_FULL_INSTANCE)/root/development-snap-package.snap
	incus exec $(INCUS_FULL_INSTANCE) -- sudo snap install --dangerous /root/development-snap-package.snap

.PHONY: incus-install-backup-artifact
incus-install-backup-artifact:
	@echo "Installing the latest backup artifact from ~/Downloads inside the Incus VM ..."
	@latest="$(shell ls -1t ~/Downloads/backups*.zip | head -1)"; \
	if [ -z "$$latest" ]; then \
		echo "No backup artifact found in ~/Downloads (looking for backups*.zip)"; \
		exit 1; \
	fi; \
	echo "Installing backup from $$latest to $(INCUS_FULL_INSTANCE) ..."; \
	unzip -p "$$latest" backups/immich_database_*.sql.xz | incus file push - $(INCUS_FULL_INSTANCE)/var/snap/immich-distribution/common/backups/database-backup.sql.xz; \
	unzip -p "$$latest" backups/immich_assets_*.tar.xz | incus file push - $(INCUS_FULL_INSTANCE)/var/snap/immich-distribution/common/backups/assets-backup.tar.xz; \
	incus exec $(INCUS_FULL_INSTANCE) -- chmod 644 /var/snap/immich-distribution/common/backups/database-backup.sql.xz /var/snap/immich-distribution/common/backups/assets-backup.tar.xz; \
	incus exec $(INCUS_FULL_INSTANCE) -- bash -c 'sudo immich-distribution.restore -y -d /var/snap/immich-distribution/common/backups/database-backup.sql.xz'; \
	incus exec $(INCUS_FULL_INSTANCE) -- bash -c 'sudo immich-distribution.restore -y -a /var/snap/immich-distribution/common/backups/assets-backup.tar.xz'; \
	incus exec $(INCUS_FULL_INSTANCE) -- rm -f /var/snap/immich-distribution/common/backups/database-backup.sql.xz /var/snap/immich-distribution/common/backups/assets-backup.tar.xz

.PHONY: incus-destroy
incus-destroy:
	incus delete -f $(INCUS_FULL_INSTANCE)

#
# This will remove remove/purge the local installation.
#

.PHONY: reset
reset:
	@echo "This will purge and clean the local installation in 5 seconds ..."
	sleep 5
	make clean
	sudo snap remove --purge immich-distribution
	sudo rm -rf prime

.PHONY: clean
clean:
	snapcraft clean || true
	rm -rf SNAP_COMMON tests/latest_logs/ *.snap

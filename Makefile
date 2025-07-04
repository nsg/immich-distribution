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

.PHONY: incus-setup
incus-setup:
	incus init images:ubuntu/24.04 immich-distribution --vm -c limits.memory=6GiB -d root,size=30GiB
	incus config device add immich-distribution build disk source=${PWD} path=/build
	incus start immich-distribution
	sleep 30 # wait for the VM to boot
	incus exec immich-distribution -- sudo apt update
	incus exec immich-distribution -- sudo apt install snapd podman make python3.12-venv curl git jq -y
	sleep 10 # wait snapd to start
	incus exec immich-distribution -- sudo snap install --classic snapcraft
	incus exec immich-distribution -- sudo snap install lxd
	incus exec immich-distribution -- sudo lxd init --auto

incus-%:
	incus exec immich-distribution -- bash -c 'cd /build && make $*'

.PHONY: incus-destroy
incus-destroy:
	incus delete -f immich-distribution

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

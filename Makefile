SNAP_FILE := $(shell ls -1t *.snap | head -1)

all: build install
	:

.PHONY: build
build:
	snapcraft --debug

.PHONY: install
install:
	sudo snap install --dangerous ${SNAP_FILE}

clean:
	rm -rf SNAP_COMMON tests/latest_logs/ *.snap

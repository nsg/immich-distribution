.PHONY: build
build:
	./build.sh v1.62.1

.PHONY: install
install:
	mkdir -p ${SNAPCRAFT_PART_INSTALL}/usr/src/ml
	mkdir -p ${SNAPCRAFT_PART_INSTALL}/opt/venv
	cp -r immich/machine-learning/app ${SNAPCRAFT_PART_INSTALL}/usr/src/ml
	cp -r /opt/venv/ml ${SNAPCRAFT_PART_INSTALL}/opt/venv

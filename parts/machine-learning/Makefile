.PHONY: build
build:
	./build.sh v1.72.0

.PHONY: install
install:
	mkdir -p ${SNAPCRAFT_PART_INSTALL}/usr/src/ml
	mkdir -p ${SNAPCRAFT_PART_INSTALL}/opt/python-libs/ml
	cp -r immich/machine-learning/app ${SNAPCRAFT_PART_INSTALL}/usr/src/ml
	cp -r /opt/venv/ml/lib/python3.11/site-packages \
		${SNAPCRAFT_PART_INSTALL}/opt/python-libs/ml/

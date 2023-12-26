IMMICH_VERSION := v1.88.2

.PHONY: build
build: immich/server/.built immich/web/.built
	echo ${PKG_CONFIG_PATH}
	pkg-config --list-all

immich/server/.built: immich/server/node_modules immich
	cd immich/server && npm run build
	cd immich/server && npm prune --omit=dev --omit=optional
	touch immich/server/.built

immich/server/node_modules: immich
	cd immich/server && npm ci

immich/web/.built: immich immich/server/.built
	patch -p0 -i ${SNAPCRAFT_PART_SRC}/../../patches/src/001-version-announcement-box.patch -d ${SNAPCRAFT_PART_BUILD}/immich
	cd immich/web \
		&& npm ci \
		&& npm run build
	touch immich/web/.built

immich:
	git clone https://github.com/immich-app/immich.git --branch ${IMMICH_VERSION} --depth 1

${SNAPCRAFT_PART_INSTALL}/usr/src/app:
	mkdir -p ${SNAPCRAFT_PART_INSTALL}/usr/src/app

.PHONY: install
install: immich/server/.installed immich/web/.installed
	:

immich/server/.installed: ${SNAPCRAFT_PART_INSTALL}/usr/src/app immich/server/.built
	cp -r immich/server/node_modules ${SNAPCRAFT_PART_INSTALL}/usr/src/app
	cp -r immich/server/dist ${SNAPCRAFT_PART_INSTALL}/usr/src/app
	cp -r immich/server/bin ${SNAPCRAFT_PART_INSTALL}/usr/src/app
	cp -r immich/server/assets ${SNAPCRAFT_PART_INSTALL}/usr/src/app
	cp immich/server/package.json immich/server/package-lock.json ${SNAPCRAFT_PART_INSTALL}/usr/src/app
	touch immich/server/.installed

immich/web/.installed: ${SNAPCRAFT_PART_INSTALL}/usr/src/app immich/web/.built
	cp -r immich/web/build ${SNAPCRAFT_PART_INSTALL}/usr/src/app/www
	touch immich/web/.installed

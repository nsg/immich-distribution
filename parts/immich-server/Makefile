IMMICH_VERSION := v1.90.2
IMMICH_REPO := https://github.com/immich-app/immich.git

#
# Triggered by Snapcraft
#

.PHONY: build
build: immich/server/dist immich/web/build
	@echo "Immich has been built"

.PHONY: install
install: immich-server-install immich-web-install
	@echo "Immich installed successfully"

#
# Generic targets
#

immich:
	git clone ${IMMICH_REPO} --branch ${IMMICH_VERSION} --depth 1 --recurse-submodules

${SNAPCRAFT_PART_INSTALL}/usr/src/app:
	mkdir -p ${SNAPCRAFT_PART_INSTALL}/usr/src/app

#
# Immich server part
#

immich/server/dist: immich/server/node_modules immich
	cd immich/server && npm run build
	cd immich/server && npm prune --omit=dev --omit=optional

immich/server/node_modules: immich
	cd immich/server && npm ci

.PHONY: immich-server-install
immich-server-install: ${SNAPCRAFT_PART_INSTALL}/usr/src/app
	cp -r immich/server/node_modules ${SNAPCRAFT_PART_INSTALL}/usr/src/app
	cp -r immich/server/dist ${SNAPCRAFT_PART_INSTALL}/usr/src/app
	cp -r immich/server/bin ${SNAPCRAFT_PART_INSTALL}/usr/src/app
	cp -r immich/server/resources ${SNAPCRAFT_PART_INSTALL}/usr/src/app
	cp immich/server/package.json immich/server/package-lock.json ${SNAPCRAFT_PART_INSTALL}/usr/src/app
	cp ${SNAPCRAFT_PART_SRC}/scripts/immich-server ${SNAPCRAFT_PART_INSTALL}/bin
	cp ${SNAPCRAFT_PART_SRC}/scripts/immich-microservices ${SNAPCRAFT_PART_INSTALL}/bin

#
# Immich web part
#

immich/web/build: immich/web/node_modules immich
	patch -p0 -i ${SNAPCRAFT_PART_SRC}/patches/001-version-announcement-box.patch -d ${SNAPCRAFT_PART_BUILD}/immich
	cd immich/web && npm run build

immich/web/node_modules: immich
	cd immich/web && npm ci

.PHONY: immich-web-install
immich-web-install: ${SNAPCRAFT_PART_INSTALL}/usr/src/app
	cp -r immich/web/build ${SNAPCRAFT_PART_INSTALL}/usr/src/app/www

VERSION=v1.98.1
SOURCE_FILE_PATH=https://raw.githubusercontent.com/immich-app/immich/${VERSION}/web/src/lib/components/shared-components/version-announcement-box.svelte

download-patch:
	wget ${SOURCE_FILE_PATH} -O src/version-announcement-box.svelte

make-patch:
	diff -u src/version-announcement-box.svelte src/version-announcement-box-snap.svelte > 001-version-announcement-box.patch || :
	sed -i "s/src\/version-announcement-box/web\/src\/lib\/components\/shared-components\/version-announcement-box/g" 001-version-announcement-box.patch

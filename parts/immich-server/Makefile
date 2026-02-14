UPSTREAM_DIR = ../../upstream/immich/server
PATCHES_DIR = patches

PATCH_FILES := $(wildcard $(PATCHES_DIR)/*.patch)

.PHONY: test

test:
	@cd $(UPSTREAM_DIR) && \
	for patch in $(PATCH_FILES); do \
		git apply --check $(CURDIR)/$$patch && echo "Patch $$patch applied successfully" || { echo "Patch $$patch failed to apply"; exit 1; }; \
	done

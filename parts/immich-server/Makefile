UPSTREAM_DIR = ../../upstream/immich/server
SRC_DIR = src
PATCHES_DIR = patches

# Find all TypeScript files under src/
SRC_FILES := $(shell find $(SRC_DIR) -name "*.ts" 2>/dev/null)
PATCH_FILES := $(patsubst $(SRC_DIR)/%.ts,$(PATCHES_DIR)/$(subst /,__,%.patch),$(SRC_FILES))

.PHONY: all clean test

all: $(PATCH_FILES)

$(PATCHES_DIR)/%.patch: $(SRC_DIR)/%.ts
	@mkdir -p $(PATCHES_DIR)
	@mkdir -p $(UPSTREAM_DIR)/src/$(dir $(patsubst $(SRC_DIR)/%,%,$<))
	cd $(UPSTREAM_DIR) && \
	[ -f src/$(patsubst $(SRC_DIR)/%,%,$<) ] && cp src/$(patsubst $(SRC_DIR)/%,%,$<) src/$(patsubst $(SRC_DIR)/%,%,$<).orig || true; \
	cp $(CURDIR)/$< src/$(patsubst $(SRC_DIR)/%,%,$<); \
	git add src/$(patsubst $(SRC_DIR)/%,%,$<); \
	git diff --cached src/$(patsubst $(SRC_DIR)/%,%,$<) > $(CURDIR)/$(PATCHES_DIR)/$(subst /,__,$(patsubst $(SRC_DIR)/%,%,$<)).patch; \
	git reset HEAD src/$(patsubst $(SRC_DIR)/%,%,$<); \
	if [ -f src/$(patsubst $(SRC_DIR)/%,%,$<).orig ]; then \
		mv src/$(patsubst $(SRC_DIR)/%,%,$<).orig src/$(patsubst $(SRC_DIR)/%,%,$<); \
	else \
		rm -f src/$(patsubst $(SRC_DIR)/%,%,$<); \
	fi

test: $(PATCH_FILES)
	@cd $(UPSTREAM_DIR) && \
	for patch in $(PATCH_FILES); do \
		git apply --check $(CURDIR)/$$patch && echo "Patch $$patch applied successfully" || { echo "Patch $$patch failed to apply"; exit 1; }; \
	done

clean:
	rm -f $(PATCHES_DIR)/*.patch

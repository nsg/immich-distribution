IMAGE = immich-distribution-docs
ZOLA_IMAGE = ghcr.io/getzola/zola:v0.21.0
HOSTNAME := $(shell hostname)
PODMAN := $(shell command -v podman 2> /dev/null || command -v docker 2> /dev/null)

run:
	$(PODMAN) run \
		-v$(shell pwd)/site:/site:z \
		--workdir /site \
		-p 1111:1111 \
		-p 1024:1024 \
		${ZOLA_IMAGE} \
			serve \
				-p 1111 \
				-i 0.0.0.0 \
				--base-url "${HOSTNAME}.lan.nsgsrv.net"

build: site/snapstore-data.json site/snapstore-metrics-chart.json site/static/js/mermaid.min.js
	rm -rf site/build-out
	$(PODMAN) run \
		-v$(shell pwd)/site:/site:z \
		--workdir /site \
		${ZOLA_IMAGE} build -o /site/build-out

site/snapstore-data.json: snapstore_versions.sh
	./snapstore_versions.sh

site/snapstore-metrics-chart.json: snapstore_metrics.sh
	@if [ -f .env ]; then . ./.env; fi && ./snapstore_metrics.sh

site/static/js/mermaid.min.js:
	mkdir -p site/static/js
	curl -sL https://cdn.jsdelivr.net/npm/mermaid@11.12.0/dist/mermaid.min.js -o site/static/js/mermaid.min.js

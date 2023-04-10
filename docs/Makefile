IMAGE := ghcr.io/getzola/zola:v0.17.2

serve:
	podman run \
		-v$(shell pwd)/site:/site \
		--workdir /site \
		-p 1111:1111 \
		-p 1024:1024 \
		${IMAGE} serve -p 1111 -i 0.0.0.0 --base-url localhost

IMMICH_VERSION := v1.82.1

# Use our own Python, over the older one in core20
export PATH := ${SNAPCRAFT_PART_BUILD}/../../dependencies/install/usr/local/bin:$(PATH)

POETRY_ENV = ${HOME}/poetry
POETRY = ${POETRY_ENV}/bin/poetry

.PHONY: build
build: immich ${POETRY_ENV}
	${POETRY} install \
		-C immich/machine-learning \
		--sync \
		--no-interaction \
		--no-ansi \
		--no-root \
		--only main

	${POETRY} run \
		-C immich/machine-learning \
		pip install \
			--no-deps \
			-r immich/machine-learning/requirements.txt

immich:
	git clone --branch ${IMMICH_VERSION} https://github.com/immich-app/immich.git

${POETRY_ENV}:
	python3 -m venv ${POETRY_ENV}
	${POETRY_ENV}/bin/pip install -U pip setuptools
	${POETRY_ENV}/bin/pip install poetry

.PHONY: install
install:
	mkdir -p ${SNAPCRAFT_PART_INSTALL}/app/machine-learning
	mkdir -p ${SNAPCRAFT_PART_INSTALL}/bin

	# Deploy application
	cp immich/machine-learning/log_conf.json ${SNAPCRAFT_PART_INSTALL}/app/machine-learning/
	cp -r immich/machine-learning/app ${SNAPCRAFT_PART_INSTALL}/app/machine-learning/app
	
	# Deploy Python packages (installed with Poetry & pip in the build step)
	cp -r $(shell ${POETRY} -C immich/machine-learning env info -p)/lib/python3.11/site-packages \
		${SNAPCRAFT_PART_INSTALL}/app/machine-learning/python-packages

	# Deploy gunicorn (installed with Poetry) and remove shebang
	cp $(shell ${POETRY} -C immich/machine-learning env info -p)/bin/gunicorn \
		${SNAPCRAFT_PART_INSTALL}/bin/gunicorn
	sed -i '1d' ${SNAPCRAFT_PART_INSTALL}/bin/gunicorn

	# Deploy immich-machine-learning script
	cp immich-machine-learning ${SNAPCRAFT_PART_INSTALL}/bin/immich-machine-learning

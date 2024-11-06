IMMICH_VERSION := v1.120.0

POETRY_ENV = ${HOME}/poetry
POETRY = ${POETRY_ENV}/bin/poetry

.PHONY: build
build: immich ${POETRY}
	${POETRY} install \
		-C immich/machine-learning \
		--sync \
		--no-interaction \
		--no-ansi \
		--no-root \
		--with cpu \
		--without dev

immich:
	git clone --branch ${IMMICH_VERSION} https://github.com/immich-app/immich.git

${POETRY_ENV}:
	python3 -m venv ${POETRY_ENV}

${POETRY}: ${POETRY_ENV}
	${POETRY_ENV}/bin/pip install -U pip setuptools
	${POETRY_ENV}/bin/pip install poetry

.PHONY: install
install:
	mkdir -p ${CRAFT_PART_INSTALL}/app/machine-learning
	mkdir -p ${CRAFT_PART_INSTALL}/app/machine-learning/ann
	mkdir -p ${CRAFT_PART_INSTALL}/bin

	# Deploy application
	cp immich/machine-learning/log_conf.json ${CRAFT_PART_INSTALL}/app/machine-learning/
	cp -r immich/machine-learning/app ${CRAFT_PART_INSTALL}/app/machine-learning/app
	cp -r immich/machine-learning/ann/ann.py ${CRAFT_PART_INSTALL}/app/machine-learning/ann/ann.py

	# Deploy Python packages (installed with Poetry & pip in the build step)
	cp -r $(shell ${POETRY} -C immich/machine-learning env info -p)/lib/python3.11/site-packages \
		${CRAFT_PART_INSTALL}/app/machine-learning/python-packages

	# Deploy gunicorn (installed with Poetry) and remove shebang
	cp $(shell ${POETRY} -C immich/machine-learning env info -p)/bin/gunicorn \
		${CRAFT_PART_INSTALL}/bin/gunicorn
	sed -i '1d' ${CRAFT_PART_INSTALL}/bin/gunicorn

	# Deploy immich-machine-learning script
	cp immich-machine-learning ${CRAFT_PART_INSTALL}/bin/immich-machine-learning

	# Mark binary or shared library as not requiring executable stack.
	# Snapcraft security policy requires that I strip the executable stack for libraries.
	execstack --clear-execstack ${CRAFT_PART_INSTALL}/app/machine-learning/python-packages/onnxruntime/capi/onnxruntime_pybind11_state.cpython-311-x86_64-linux-gnu.so

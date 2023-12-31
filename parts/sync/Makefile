PYTHON_PATH = ${CRAFT_PART_BUILD}/../../python/install/usr/local/bin
PYTHON_ENV = ${CRAFT_PART_INSTALL}/opt/pipsyncenv
PIP = ${PYTHON_PATH}/python3 ${PYTHON_PATH}/pip3

export PATH := ${PYTHON_PATH}:$(PATH)

build:
	python3 --version
	${PIP} --version

install:
	${PIP} install watchfiles requests psycopg2-binary pyyaml --target ${PYTHON_ENV}

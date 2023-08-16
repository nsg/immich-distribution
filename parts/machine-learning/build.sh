#!/bin/bash

VERSION="$1"
PYTHON_PART_INSTALL_BIN="${PWD}/../../dependencies/install/usr/local/bin"

mkdir -p /opt/venv/

python() {
    $PYTHON_PART_INSTALL_BIN/python3 $@
}

pip() {
    python $PYTHON_PART_INSTALL_BIN/pip3 $@
}

[ -d immich ] || git clone --branch $VERSION https://github.com/immich-app/immich.git
[ -d "/opt/venv/ml" ] || python -m venv "/opt/venv/ml"
[ -d "/opt/venv/poetry" ] || python -m venv "/opt/venv/poetry"

/opt/venv/poetry/bin/python --version
/opt/venv/poetry/bin/pip install poetry

# Configure Poetry and install dependencies
cd immich/machine-learning

export VIRTUAL_ENV="/opt/venv/ml"
/opt/venv/poetry/bin/poetry config installer.max-workers 10
/opt/venv/poetry/bin/poetry config virtualenvs.create false
/opt/venv/poetry/bin/poetry install --sync --no-interaction --no-ansi --no-root --only main
unset VIRTUAL_ENV

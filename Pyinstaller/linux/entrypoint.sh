#!/bin/bash -i

set -e

WORKDIR=${SRCDIR:-/src}

cd $WORKDIR

if [ -f poetry.lock ]; then
    poetry install
fi

echo "$@"

if [[ "$@" == "" ]]; then
    poetry run pyinstaller --clean -y --dist ./dist/linux --workpath /tmp --onefile awslogin.spec
    chown -R --reference=. ./dist/linux
else
    sh -c "$@"
fi

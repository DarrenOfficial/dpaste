#!/bin/bash

set -ex

ARGS=

if [[ ${DRY_RUN:-0} -eq 1 ]]; then
  ARGS="--dry-run"
fi

python3 manage.py cleanup_snippets $ARGS

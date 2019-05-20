#!/bin/bash

set -ex

python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:5000


#!/bin/bash

set -ex

cp contribute.json build/

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic
gunicorn3 --bind 0.0.0.0:5000 dpaste.wsgi
#python3 manage.py runserver 0.0.0.0:5000


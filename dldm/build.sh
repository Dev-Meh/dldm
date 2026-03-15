#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python "dldm/manage.py" collectstatic --noinput
python "dldm/manage.py" migrate


#!/bin/bash

python ./beacon/admin-ui/manage.py reset_db
python ./beacon/admin-ui/manage.py migrate
python ./beacon/admin-ui/manage.py runserver 0.0.0.0:8000
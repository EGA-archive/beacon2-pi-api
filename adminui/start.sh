#!/bin/bash

python ./adminui/manage.py reset_db
python ./adminui/manage.py makemigrations
python ./adminui/manage.py migrate
python ./adminui/manage.py runserver 0.0.0.0:8000
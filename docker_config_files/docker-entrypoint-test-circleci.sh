#!/bin/bash
cp catalogue_service/settings_local.py.default catalogue_service/settings_local.py
python manage.py migrate 
python manage.py test


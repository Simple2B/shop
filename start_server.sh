#!/bin/sh

echo Initiating database ...
flask db init
echo Migrating ...
flask db migrate
echo Applying migrations ...
flask db upgrade
echo Running app
flask run -h 0.0.0.0 \n
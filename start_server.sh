#!/bin/sh
# echo Run db upgrade
# flask db upgrade
echo Run app
flask createdb
flask seed
flask run -h 0.0.0.0
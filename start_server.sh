#!/bin/sh
echo Run db upgrade
flask db upgrade
echo Running app
flask run -h 0.0.0.0

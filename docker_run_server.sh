#!/bin/sh
docker-compose down
docker-compose up --build
docker-compose exec web python manage.py makemigrations djangospider
docker-compose exec web python manage.py migrate
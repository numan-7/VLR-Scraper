#!/bin/sh
docker-compose down
docker-compose up --build -d
docker-compose exec web python manage.py makemigrations djangospider
docker-compose exec web python manage.py migrate
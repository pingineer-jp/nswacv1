#!/bin/sh

docker-compose up -d --build
docker cp ~/.nii-socs python3:/root/
#docker-compose exec python3 bash
docker exec -it python3 python nswacv1/nswacv1.py
#docker-compose down

docker pull rlukovnikov/ya-hw-bot
docker tag rlukovnikov/ya-hw-bot yabot
docker run --name yabot --env-file .env --restart always --detach yabot
docker logs yabot
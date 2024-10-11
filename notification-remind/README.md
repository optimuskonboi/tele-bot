# notification_telegram

  pip install python-telegram-bot

  pip install python-telegram-bot[job-queue]


docker build -t vns-remind .

docker network create --ipv6=false no_ipv6_network
docker run -d --restart=always --network=no_ipv6_network --name vns-remind vns-remind


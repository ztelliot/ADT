FROM ubuntu:latest

WORKDIR /usr/src/app

COPY . .
RUN apt update && apt install -y git python3 python3-pip nginx cron && apt clean && rm -rf /var/lib/apt/lists/* && pip3 install --no-cache-dir -r requirements.txt && chmod +x ./docker-entrypoint.sh

EXPOSE 2333
EXPOSE 80

ENV LC_ALL C.UTF-8
ENTRYPOINT ["./docker-entrypoint.sh"]

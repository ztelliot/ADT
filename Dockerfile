FROM ubuntu:latest

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt update && apt install -y git python3 python3-pip && apt clean && pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 2333
EXPOSE 80

CMD [ "python3", "./main.py" ]
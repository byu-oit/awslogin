FROM ubuntu:16.04

RUN apt-get update \
    && apt-get upgrade -y

RUN apt-get install python3 python3-pip python3-venv -y

RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install poetry

COPY entrypoint.sh /entrypoint.sh

VOLUME /src/
WORKDIR /src/

ENTRYPOINT ["/entrypoint.sh"]

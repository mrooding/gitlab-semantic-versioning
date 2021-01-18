FROM python:3.7-slim-stretch

RUN set -ex \
    \
    && apt-get -y upgrade \
    && apt-get -y update \
    && apt-get -y install git \
    && apt-get clean

WORKDIR /version-update

COPY /requirements.txt .

RUN pip install -r requirements.txt

COPY /version-update.py .

COPY /bump-version /usr/bin/bump-version

RUN chmod +x /usr/bin/bump-version

CMD ["bump-version"]

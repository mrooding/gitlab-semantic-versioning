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

RUN echo 'alias bump_version="python3 /version-update/version-update.py"' >> /root/.bashrc

COPY /version-update.py .

CMD ["python", "/version-update.py"]

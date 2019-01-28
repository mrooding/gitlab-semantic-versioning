FROM python:3.7

RUN apt-get -y upgrade && \
    apt-get -y install git && \
    apt-get clean

WORKDIR /version-update

COPY /requirements.txt .

RUN pip install -r requirements.txt

COPY /version-update.py .

CMD ["python", "/version-update.py"]

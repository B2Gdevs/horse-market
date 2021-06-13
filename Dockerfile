FROM python:3.6

RUN apt-get update && apt-get -y install curl postgresql-client

WORKDIR /app

COPY ./requirements.txt /app
RUN pip3 install --upgrade pip -r requirements.txt

COPY . /app

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]

CMD python3 manage.py runserver 0.0.0.0:8000
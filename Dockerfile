FROM python:3.7-slim-buster

RUN apt-get update
RUN apt-get install -y libpq-dev openssl libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /code
WORKDIR /code

RUN pip install -r requirements.txt

EXPOSE 8000
CMD python ./manage.py runserver

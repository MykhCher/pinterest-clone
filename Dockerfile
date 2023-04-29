# python base image
FROM python:3.10.11-alpine

# env setting
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# setting workdir
WORKDIR /code

# configuring dependencies and workdir
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
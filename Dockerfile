# =======
# BUILDER
# =======

# python base image
FROM python:3.10.11-alpine as builder

# env setting
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# setting workdir
WORKDIR /code

# copy entrypoint
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh 

# configuring dependencies and workdir
RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /code/wheels -r requirements.txt
COPY . /code/

# run entrypoint.sh
ENTRYPOINT ["/code/entrypoint.sh"]

# =====
# FINAL
# =====

# pull official base image
FROM python:3.10.11-alpine

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
COPY ./media $APP_HOME/mediafiles
WORKDIR $APP_HOME

# install dependencies
RUN apk update && apk add libpq
COPY --from=builder /code/wheels /wheels
COPY --from=builder /code/requirements.txt .
RUN pip install --no-cache /wheels/*

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# run entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]
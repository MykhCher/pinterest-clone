# Pinterest Clone Pet Project

This is pet project, developed to apply knowledge about different techs on practice. 
Here is the list of techs that been used on this project:
 - Python 3.10.11
 - Django 4.2
 - Django REST Framework 3.14
 - PostgreSQL (using psycopg2-binary==2.9.6 to work with db via docker)
 - Redis 4.6.0
 - nginx (latest version from Docker Images)
 - Gunicorn
 - Docker
 - docker-compose

## How to setup project locally

First of all, clone this project from GitHub repository:
```sh
$ git clone https://github.com/MykhCher/pinterest-clone.git pinterest-clone
$ cd pinterest-clone
```
Now, when you have it installed on your machine, set up virtual environment and install all dependencies.

For Ubuntu:
```sh
$ python -m venv env
$ source env/bin/activate
```
For Windows:
```sh
$ python -m venv env
$ env/Scripts/activate
```
Install dependencies from `requirements.txt` file:
```sh
$ pip install -r requirements.txt
```

### Creating Mailtrap account

There is a mail-sending logic implemented in this app, so if you want to test it, you should have a service, that supports
sending email. If you dont have one, you can use [Mailtrap](https://mailtrap.io/register/signup?ref=header). 
After you sign up, head up for the [Email Testing](https://mailtrap.io/inboxes) page, visit the `My Inbox` (or create new)
and in `Integrations` window choose `Django` option. Your credentials and other options will be provided. 
To see your password, choose `Show credentials` option, which is above the Integrations window.

### .env.prod file
After we installed all the dependencies, we should do one more thing in order for project to work properly.
In `docker-compose.yml` you can see, that all environment variables are configured via `.env.prod` file.
So lets create `.env.prod` file in the projects root directory.
Add the next content to the `.env.prod` file:
```.env.prod
# Django settings.
DEBUG=1
SECRET_KEY='your-django-secure-key'
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1

# Database settings.
POSTGRES_PASSWORD=postgres
POSTGRES_USER=postgres
POSTGRES_NAME=postgres
POSTGRES_DB=postgres
SQL_ENGINE=django.db.backends.postgresql
SQL_HOST=db
SQL_PORT=5432
DATABASE=postgres

# SMTP credentials.
EMAIL_PORT=2525
EMAIL_HOST='sandbox.smtp.mailtrap.io'
EMAIL_HOST_USER='your-username'         # Your Mailtrap 
EMAIL_HOST_PASSWORD='your-password'     # user account credentials.
```

Take care of SMTP credentails and paste your username and password instead of `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`
accordingly.

### Run project.
After you saved changes into your `.env.prod` file, you can run the project. Run:
```sh
$ docker-compose up -d --build
```


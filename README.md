# Runner Database Demo

This is a demo runner database for the RCS Gugulethu Athletics Club. It allows you to predict race times on synthetic data. You can search for a runner such as Karabo Khumalo, Lethabo Ndlovu, and Bandile Nkosi (fake runners) and get the predicted race time.

The app is hosted on Heroku https://runner-db-demo.herokuapp.com/

## Table of Contents 
  * [Setup](#setup)
    + [Docker](#docker)
    + [Docker Compose](#docker-compose)
  * [Data](#data)
  * [Prediction](#prediction)
  * [Running the tests](#running-the-tests)
    + [Database tests](#database-test)
    + [View function tests](#view-function-tests)
  * [Deployment](#deployment)
    + [Heroku Postgres](#heroku-postgres)


## Setup
The app was created with Python 3.7.5, but Python 3.5 or later should probably work. Make a virtual environment in your project directory like so:
```bash
virtualenv -p python3.7 .venv
```
Activate the environment with 
```bash
source .venv/bin/activate
```
The `python-Levenshtein` package in `requirements_ts.txt` requires `python3-dev` to be installed first (`sudo apt install python3-dev`) before running the `pip install` commands. 

Once done, install the necessary packages in your virtualenv with 
```bash
pip install -r requirements.txt
pip install -r requirements_ts.txt
```

### Docker
The Flask app and associated database live inside Docker containers. Docker installation instructions can be found [here](https://docs.docker.com/install/). Note that if you are using an older version of Windows or Windows 10 Home, you will need to install [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/). A helpful guide to get this working with Windows Subsystem for Linux is [here](https://nickjanetakis.com/blog/setting-up-docker-for-windows-and-wsl-to-work-flawlessly).

Once installation is done, create your Docker machine
```bash
docker-machine create --driver virtualbox <name>
```
and set the environment variables
```bash
eval $(docker-machine env <name>)
```
. Or add the output of `docker-machine env <name>` to your `.bashrc`. 

To start your machine, run 
```bash
docker-machine start <name>
```

### Docker Compose

Make a `docker-compose.yml` file that will create Flask and Postgres containers. Here is a snippet for the Flask container.
```dockerfile
version: '3.7' 

services:
  web:
    container_name: flask_sqlalchemy
    build: 
      context: .
    # Useful for debugging
    entrypoint: ["sh", "-c", "sleep 2073600"]
    ports:
      - "5000:5000"
    volumes:
      - ./runner_app:/code/
    environment: 
      - FLASK_ENV=$FLASK_ENV
    depends_on:
      - database  
    ...
```
You can define multiple services under the `services` heading such as `web` or `database`. You can also have services depend on each other under the `depends_on` heading. The environment variable `FLASK_ENV` will be set to `development` or `production` from the terminal, determining the config to be used.

The `docker-compose.yml` file references a Dockerfile that will pull a base image to work from. It includes a `requirements.txt` file that lists the packages to be installed into the container. The Dockerfile should be in the same directory as the `docker-compose.yml` file. The location of the Dockerfile can also be specified under the `build` heading and `context` subheading. Some examples of how to write Dockerfiles can be found [here](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

Once the Dockerfile and `docker-compose.yml` are ready, run
```bash
docker-compose up --build -d
```
This will build your images and run the containers in detached mode. The status of your containers can be viewed using 

```bash
docker ps -a
```
and your images with 

```bash
docker images
```

To run the flask application in the container, run

```bash
docker exec -it <name_of_flask_container> python <name_of_app_script>.py
```

For example, 
```bash
docker exec -it flask_sqlalchemy python wsgi.py
```

If you prefer to have the app start after container creation, simply comment out the `entrypoint` configuration option. 

The app should be running on localhost at the specified port. If you are using `Docker Toolbox`, this may not be accessible on localhost. You will have to get the IP of your docker machine with `docker-machine ip`, and then type the resulting IP into your browser with the appropriate port, for example `192.168.99.100:5000`.

### .env file
The `database` service in `docker-compose.yml` will read the database settings from a `.env` file. Create a `.env` file in the top level directory and add something such as

```
POSTGRES_USER=db_user
POSTGRES_HOST=database
POSTGRES_DB=some_db
POSTGRES_PORT=5432
POSTGRES_PASSWORD=foobar
```
The `POSTGRES_HOST` variable is the same name as the service for the `Postgres` container in `docker-compose.yml`, in this case `database`.

## Data 
The data is generated with in `data/gen_data.py`. The data is drawn from a normal distribution with a standard deviation of 15 minutes. 

To seed the postgres database running inside a docker container, start the docker containers with 
```
docker compose up -d
``` 
and then run 
```
docker exec -it <web_service_container_name> python data/gen_data.py
```
When viewing the app on localhost, you will be able to get the race predictions.

## Prediction
The race predictions are made using an ARIMA time series model. For now, the parameters for the ARIMA model are set automatically with the `auto_arima` function in the [`pmdarima`](https://alkaline-ml.com/pmdarima/modules/generated/pmdarima.arima.auto_arima.html) package. It seeks to find the parameters that minimize AIC. Cross validation is done with a rolling forecast orgin. 

## Running the tests

Set `FLASK_ENV` to `testing`. You will also need to make sure the testing database is up in a docker container. To do this, run `docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d`. After the containers are running, use `pytest -v`. The `--disable-warnings` flag can be added to suppress warnings output.

### Database tests

The tests found in `tests/test_db.py` test whether a new user can be successfully added to the database

To run these tests only, use
```bash
pytest -v tests/test_db.py
```

### View function tests

The tests in `tests/test_wsgi.py` test the view functions in `routes.py`. They test the following:

- Proper loading of Home Page
- Login and Logout for Admin Users
- Race prediction by runner

Each test checks that the response code is 200 and that the correct output is returned.

To run these tests, use
```
pytest -v tests/test_wsgi.py
```

## Deployment

The app is deployed on Heroku. The Heroku CLI installation instructions can be found [here](https://devcenter.heroku.com/articles/heroku-cli).

Start by logging in using `heroku login`. If you are deploying with Docker, you may also need to log in with `heroku container:login`. Your Docker containers can be pushed to Heroku with the `heroku container:push --app <name>` command. Afterwards, you can release this container with `heroku container:release --app <name>`. In my push command, I set `FLASK_ENV` to `production` and run `heroku container:push web --app <name> --arg FLASK_ENV_ARG=$FLASK_ENV`. This will get picked up by the Dockerfile so that the proper config settings are used. An alternative would be to have separate Dockerfiles for development and production. 

For deployment without Docker, see these [instructions](https://devcenter.heroku.com/categories/deployment).

### Heroku Postgres
You will also need to provision a [Heroku Postgres](https://devcenter.heroku.com/articles/heroku-postgresql) instance with 

```bash
heroku addons:create heroku-postgresql:<PLAN-NAME>
```
such as `heroku addons:create heroku-postgresql:hobby-dev`.

To load data to the Heroku Postgres instance, first make a backup of your local Postgres data 

```bash
docker exec <name_of_postgres_container> pg_dump -U <username> -d <dbname> > backup.sql
```

Then add it to the Heroku Postgres instance with 
```bash
heroku pg:psql --app <name> < backup.sql
```

There are probably better ways to do this, but I have not explored them yet.

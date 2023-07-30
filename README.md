# Move the Chains (MTC) Football

Move the Chains is a web-based (American) football simulation engine built with Python, Django, Bootstrap and Vanilla JS.

![A screenshot of the divisional standings page](screenshots/divisional-standings.png)

In its current state, the project can be better described as a simulation engine than a management simulation game (such as Football Manager), although the ultimate goal is to reach a playable state.

For example, you can simulate full seasons including playoffs but the game results are based on a random coin flip. Game statistics and management functions like trading or free agent signing have also yet to be added.

The engine does, however, support scheduling, standings, regular season / playoff matchups, team creation, player generation, and more.

The reasoning behind this approach was to make the game functional as quickly as possible. Once the league operations and management portions of the game are built out to a substantial level, then the simulation engine can be improved upon incrementally without sacrificing playability.

## Is there a hosted version?

Not currently. There are plans to release a publicly hosted beta version of the game eventually. However, the management portion of the game still needs some work before that can happen. A basic simulation engine would be a nice touch as well so the game results aren't so random.

You are welcome to run a version locally to test it out in the meantime. With that said, please don't host your own public version of the code anywhere. Feel free to review the [LICENSE.md](https://github.com/wjh18/mtc-football/blob/master/LICENSE.md) for more guidelines surrounding this limitation.

Please see the installation instructions below for details on how to setup a local version of the game for testing purposes.

## Installation Options

The most convenient way to set up your development environment is with [Docker](#docker-setup). To do so, you'll need to have Docker installed on your machine. You can [download Docker Desktop](https://www.docker.com/products/docker-desktop/) from the official site if you haven't already.

Alternatively, the project also supports a [local setup](#local-setup) with a Python virtual environment and local PostgreSQL database.

Either way, start off by forking, cloning, downloading or using (generating a new repo with) the template.

## Environment Variables

Environment variables are used to provide the container (via Docker environment variables) or local Python application (via `python-dotenv`) with context-specific environment details.

First, copy the contents of `.env.example` to a `.env` file in your project root.

```shell
cat .env.example >> .env
```

Next, generate a secret key and update the following fields in `.env`.

*Note: Django has a utility function to help with this in `django.core.management.utils` called `get_random_secret_key`, but if you don't have Django installed any random value will suffice in development to start out. You can generate a new secret key later if necessary once your container is running.*

For Docker development:

```text
DJANGO_SECRET_KEY=foo
DJANGO_POSTGRES_NAME=your_db_dev
DJANGO_POSTGRES_USER=your_db
DJANGO_POSTGRES_PASS=your_db
DJANGO_POSTGRES_HOST=db
GTM_ID=GTM-XXXXXX
FA_KIT_ID=XXXXXXXXXX
```

For local development:

```text
DJANGO_SECRET_KEY=foo
DJANGO_POSTGRES_NAME=your_db_dev
DJANGO_POSTGRES_USER=your_db
DJANGO_POSTGRES_PASS=your_db
DJANGO_POSTGRES_HOST=127.0.0.1
GTM_ID=GTM-XXXXXX
FA_KIT_ID=XXXXXXXXXX
```

Note the difference between `DJANGO_POSTGRES_HOST` in Docker vs. local setup. `GTM_ID` is only necessary in a production environment and `FA_KIT_ID` is optional unless you want to use Font Awesome icons.

## Makefile

Use `make` from the CLI to automate common commands used in project setup and administration. See `Makefile` for details.

## Docker Setup

Here's how to get set up with Docker. Skip this section if using a local environment.

If necessary, update the permissions of the entrypoint file (they should be tracked by git so it may not be necessary):

```shell
chmod +x entrypoint.sh
```

Build the image and stand up the container in detached mode (this may take a few minutes):

```shell
docker-compose build
docker-compose up -d
```

Check to make sure the containers are running and the images / Postgres volume were created. There should be two images, `<your-project>-web` and `postgres`.

Once you've confirmed this, flush and migrate the database from within the container:

```shell
docker-compose exec web python manage.py flush --no-input
docker-compose exec web python manage.py migrate
```

Next, build the frontend in development mode with `npm` (see `package.json` for details):

```shell
docker-compose exec web npm install # Install dependencies
docker-compose exec web npm run dev # Build
docker-compose exec web npm run dev-watch # Build and watch
```

You can also run the above locally outside of the container if you wish.

Lastly, create a superuser:

```shell
docker-compose exec web python manage.py createsuperuser
```

How to tear down the container after the initial build and stand it back up:

```shell
docker-compose down
docker-compose up -d
```

How to rebuild the container and stand it back up in detached mode in one command (required if changing env variables or adding a new package):

```shell
docker-compose up -d --build
```

## Local Setup

The local instructions are similar to the Docker instructions with a few distinct differences.

After cloning the repo, you should create a virtual environment at the project root and install the dependencies:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements/requirements.txt -r requirements/dev-requirements.txt
```

Next, create a local Postgres DB and user by launching `psql` from the command line. The exact commands may differ depending on your PostgreSQL version.

```postgresql
CREATE DATABASE <db_name>_dev;
CREATE USER <db_name>;
ALTER USER <db_name> WITH PASSWORD '<db_name>';
GRANT ALL PRIVILEGES ON DATABASE <db_name>_dev TO <db_name>;
ALTER USER <db_name> CREATEDB; /* Required step for PostgreSQL 15+ */
ALTER DATABASE <db_name>_dev OWNER TO <db_name>; /* Required step for PostgreSQL 15+ */
```

Migrate the db, build the frontend (requires `npm`), run the server, and create a superuser:

```shell
python manage.py migrate
npm install
npm run dev
python manage.py createsuperuser
python manage.py runserver
```

See the Docker instructions for further details on each step, but run the commands locally in a venv instead of in the container.

## Getting Started

From the homepage, log in to the superuser you created and make sure you can access `http://localhost:8000/admin`. You can also login via the Django Admin itself or use the signup flow to create a user without admin access.

*Note: Admins bypass the email verification workflow by default. For regular users, you can find email verifications in the console/shell. Unverified accounts will be unable to log in until they confirm their email.*

While in the admin, feel free to update your site domain and name at `http://localhost:8000/admin/sites/site/`. These site fields are provided to the global request context via a context processor. They can be accessed from templates with `site.domain` and `site.name`. In development, setting domain to `localhost:8000` or whatever port you're running the server on is best practice.

Additionally, update your site settings/metadata at `http://localhost:8000/admin/core/sitesettings/`. These site fields can also be accessed from the global request context with `site.settings.*`. They store various bits of metadata used for SEO in the HTML `<head>`.

## Managing Dependencies

This project uses `pip-tools` and `pip` to manage Python dependencies.

Simply pin any additional requirements you need to the `requirements/requirements.in` file and run `pip-compile requirements/requirements.in` to compile them to `requirements/requirements.txt`.

For development dependencies, the same process applies but using `dev-requirements.*`.

If using Docker, rebuild your image to install the new dependencies. For local environments, you can install them with `pip install -r requirements/requirements.txt -r requirements/dev-requirements.txt` with your virtual environment active.

In production, only install `requirements.txt`.

## Python tooling

Run these in your container or with your virtual environment active.

- Make sure tests are passing with the `pytest` command.
- Run coverage checks with `pytest --cov`
- ~~Run python package vulnerability checks with `safety check`~~ `safety` currently excluded from dependencies due to compatibility issue/bug
- Sort Python imports with `isort .`
- Format Python code with `black .`
- Lint Python code with `flake8`
- Run Python code security checks with `bandit -c pyproject.toml -r .`
- Skip pre-commit checks with `--no-verify` flag after commit message
- Run black, isort, flake8 and bandit checks automatically on commit by installing pre-commit hooks with `pre-commit install` and testing them with `pre-commit run --all-files`

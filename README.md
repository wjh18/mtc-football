# Move the Chains (MTC) Football

Move the Chains is a web-based (American) football simulation game built with Python, Django, Bootstrap and Vanilla JS.

![A screenshot of the divisional standings page](screenshots/divisional-standings.png)

Although it's semi-playable in its current state, a lot of work still needs to be done before a production version can be released.

Currently, you can simulate full seasons but the game results are based on a random coin flip. Game statistics and management functions like trading or free agent signing have also yet to be added.

In its current state, the game is really just a simple football matchup engine with a schedule, standings, playoffs, teams, and placeholder players.

The reasoning behind this was to make the game functional as quickly as possible. Once the league operations and management portions of the game are built out to a substantial level, then the simulation engine can be improved upon incrementally without sacrificing playability.

## Is there a hosted version of the game?

Not currently. There are plans to release a publicly hosted beta version of the game eventually. However, the management portion of the game still needs some work before that can happen. A basic simulation engine would be a nice touch as well so the game results aren't so random.

You are welcome to run a version locally to test it out in the meantime. With that said, please don't host your own public version of the code anywhere. Feel free to review the [LICENSE.md](https://github.com/wjh18/mtc-football/blob/master/LICENSE.md) for more guidelines surrounding this limitation.

See the installation instructions below for details on how to setup a local version of the game for testing purposes.

## Installation Options

The easiest way to set up the project is with Docker. To do so, you'll need to have Docker installed on your machine. You can download Docker Desktop from the official site.

Alternatively, you can use pip-tools and venv to manage your Python dependencies manually. There is a `requirements.in` file in the `requirements/` directory that you can run `pip-compile requirements/requirements.in` on to update dependencies if needed. Otherwise, simply install them with `pip install -r requirements.txt` after you've activated your virtual environment. You'll also need to install PostgreSQL and create a database. None of this is necessary if using Docker.

## Install with Docker

Fork the repository and clone your fork (if contributing), otherwise just clone it:

```shell
git clone https://github.com/wjh18/mtc-football.git
cd mtc-football
```

Run the following management command to initialize your project locally.

```shell
python manage.py init_local mtc_football
```

Where `mtc_football` is the db name and details. If you use anything other than `mtc_football`, make sure to update the environment variables in `docker-compose.yml` with the appropriate values as well.

This command will generate a secret key and create a `.env.dev` file at the root of your project. If the generated secret key has any `$` in it, escape them with an additional `$` (`$$`) or remove them.

You could also manually generate a secret key with `django.core.management.utils.generate_secret_key()`, create the file, and input your db creds with the following. The command is for convenience's sake.

```shell
touch .env.dev
```

The recommended contents of `.env.dev`:

```text
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=foo
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
DJANGO_SQL_ENGINE=django.db.backends.postgresql
DJANGO_SQL_DATABASE=mtc_football_dev
DJANGO_SQL_USER=mtc_football
DJANGO_SQL_PASSWORD=mtc_football
DJANGO_SQL_HOST=db
DJANGO_SQL_PORT=5432
```

If necessary, update the permissions of the entrypoint file (this should be stored by git so it may not be necessary):

```shell
chmod +x entrypoint.sh
```

Build the image and stand up the container in detached mode (this may take a few minutes):

```shell
docker-compose build
docker-compose up -d
```

Check to make sure the containers are running and the images / Postgres volume were created. There should be two images, `mtc-football-web` and `postgres`.

Once you've confirmed this, flush and migrate the database:

```shell
docker-compose exec web python manage.py flush --no-input
docker-compose exec web python manage.py migrate
```

Lastly, create a superuser:

```shell
docker-compose exec web python manage.py createsuperuser
```

Now you should be able to login with your superuser via the GUI or Django Admin at localhost:8000. You can also use the signup flow to create a user but you won't be able to log into the Django Admin with it.

How to tear down the container after the initial build and stand it back up:

```shell
docker-compose down
docker-compose up -d
```

How to rebuild the container and stand it back up in detached mode in one command (required if changing env variables or adding a new package):

```shell
docker-compose up -d --build
```

That's it! Now you can create a league, select a team, simulate a few seasons or explore the UI. Whatever your heart desires.

## How to Contribute

Please see [CONTRIBUTING.md](https://github.com/wjh18/mtc-football/blob/master/CONTRIBUTING.md) for details on how to contribute to the codebase.

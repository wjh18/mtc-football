# Contributing

To contribute code to the project, please download the [CLA-individual.md](https://github.com/wjh18/mtc-football/blob/master/CLA-individual.md) file (or [CLA-entity.md](https://github.com/wjh18/mtc-football/blob/master/CLA-entity.md) for orgs) in the root of the repository, fill in your details at the bottom, and email the completed document to [contact@mtcfootball.com](mailto:contact@mtcfootball.com).

This is a necessary step due to the licensing limitations of the software. Please see [LICENSE.md](https://github.com/wjh18/mtc-football/blob/master/LICENSE.md) for more details.

Then fork the project, clone your fork, add it as a remote to the upstream repo, make your changes on a new branch, and issue a pull request. You can also create an issue in the issue tracker for discussions about possible feature upgrades or bug fixes.

If you're new to this process, I found [this guide](https://opensource.guide/how-to-contribute/) to be a great resource.

## Installation

The project uses Docker / docker-compose for local development and Pipenv to manage Python dependencies. You will need to install Docker locally for the most streamlined setup experience. In the future, more flexible ways to spin up a development environment will be added for those who prefer alternative tools like pip and requirements.txt.

Fork the repository and clone your fork (if contributing) or clone the original repository (if testing only):

`git clone https://github.com/wjh18/mtc-football.git`

`cd mtc-football`

Create a local env file:

`touch .env.dev`

Add the following to `.env.dev`:
```
DJANGO_SECRET_KEY={SECRET_KEY}
DJANGO_DEBUG=True
```

Build the image and stand up the container in detached mode (this may take a few minutes):

`docker-compose up -d --build`

To generate a random secret key, use the following:

`docker-compose exec web python manage.py shell`
```python
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()
```

Copy the secret key into your `.env.dev` file without the single quotes.

Migrate the database:

`docker-compose exec web python manage.py migrate`

Create a superuser:

`docker-compose exec web python manage.py createsuperuser`

Now you should be able to login with your superuser via the GUI or Django Admin. You can also use the signup flow to create a user but you won't be able to log into the Django Admin with it.

That's it! Now you can create a league, select a team, simulate a few seasons or explore the UI. Whatever your heart desires.

*Note: django-debug-toolbar is installed by default which slows down page load significantly. To improve performance, uncheck all the boxes in the sidebar GUI.*
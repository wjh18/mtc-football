web = docker-compose exec web
manage = ${web} python manage.py
up = docker-compose up -d

down:
	docker-compose down

up:
	$(up)

restart:
	docker-compose down
	$(up)

build:
	$(up) --build

superuser:
	$(manage) createsuperuser

checkmigrations:
	$(manage) makemigrations --check --no-input --dry-run

migrations:
	$(manage) makemigrations

migrate:
	$(manage) migrate

flush:
	$(manage) flush --no-input

venv:
	python3 -m venv .venv
	source .venv/bin/activate

pip-sync:
	pip install --upgrade pip
	pip-sync requirements.txt dev-requirements.txt

pip-update:
	pip install --upgrade pip pip-tools
	pip-compile requirements/requirements.in
	pip-compile requirements/dev-requirements.in
	pip-sync requirements.txt dev-requirements.txt

npm-install:
	$(web) npm install

npm-dev:
	$(web) npm run dev

npm-watch:
	$(web) npm run dev-watch

test:
	$(manage) test

pytest:
	$(web) pytest --cov

pre-commit:
	pre-commit install
	pre-commit run --all-files

lint:
	flake8
	# mypy .
	bandit -c pyproject.toml -r .

format:
	isort .
	black .

shell-plus:
	$(manage) shell_plus

graph:
	$(manage) graph_models -a -o myapp_models.png
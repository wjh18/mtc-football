# Started with this tutorial's Dockerfile as a base:
# https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/

# pull official base image
FROM python:3.11-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install package dependencies
# git is needed for running pre-commit hooks and isort with skip_gitignore in container
RUN apk update \
    && apk add npm git postgresql-dev pkgconfig graphviz graphviz-dev ttf-freefont gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements/*.txt .
RUN pip install -r requirements.txt -r dev-requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["sh", "/usr/src/app/entrypoint.sh"]
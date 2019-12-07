FROM node:lts as staticfiles

ARG BUILD_EXTRAS=production

RUN echo "\nℹ️  Building staticfiles with "${BUILD_EXTRAS}" dependencies.\n"

WORKDIR /app

# Install the JS dependencies
COPY package.json package-lock.json Makefile ./

RUN if [ "$BUILD_EXTRAS" = "dev" ] ; then npm install --ignore-scripts ; else npm ci --ignore-scripts ; fi

# Copy the client/ directory and compile them. The Python application
# doesn't need to exist yet.
COPY client ./client

RUN mkdir -p dpaste/static
RUN make css
RUN make js

# ------------------------------------------------

FROM python:3.6 as build

ARG BUILD_EXTRAS=production

ENV PORT=8000

RUN echo "\nℹ️  Building Django project with "${BUILD_EXTRAS}" dependencies.\n"

WORKDIR /app

# Upgrade pip, the Image one is quite old.
RUN pip install pip==19.3.1

# Copy the dpaste staticfiles to this image
COPY --from=staticfiles /app /app/

# Copy only the files necessary to install the dpaste project as an editable
# package. This improves caching.
COPY setup.py setup.cfg ./
COPY dpaste/__init__.py dpaste/
RUN pip install -e .[${BUILD_EXTRAS}]

# Django 3.0 Fix for django-csp, which wasn't released yet
RUN pip uninstall django-csp -y
RUN pip install https://github.com/mozilla/django-csp/archive/master.zip

# Copy the rest of the application code
COPY . .

# Collect all static files once.
RUN ./manage.py collectstatic --noinput

# By default run it with pyuwsgi, which is a great production ready
# server. For development, docker-compose will override it to use the
# regular Django runserver.
CMD ./manage.py pyuwsgi --http=:${PORT} --logger file:/var/log/uwsgi.log

EXPOSE ${PORT}

FROM node:10-alpine as webbuilder

WORKDIR /usr/src/app

COPY web/rollup.config.js ./
COPY web/package*.json ./

RUN npm install

COPY web/src ./src
COPY web/public ./public

RUN npm run-script build

# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.7-slim

# Install production dependencies.
COPY ./requirements.txt ./
RUN pip install -r /requirements.txt

# Copy local code to the container image.
# ENV APP_HOME /app
# WORKDIR $APP_HOME
WORKDIR /
COPY ./agentapp /agentapp

# TODO multistage build for web
COPY --from=webbuilder /usr/src/app/public /agentapp/static

ENV PORT=8080
# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --preload --bind :$PORT --workers 1 --threads 8 agentapp:app
FROM python:3.11.0-slim-bullseye

RUN python -m pip install --upgrade pip
COPY requirements.txt /tmp
RUN python -m pip install -r /tmp/requirements.txt

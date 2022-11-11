FROM python:3.11.0-slim-bullseye

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
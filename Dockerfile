FROM python:3.8-slim

RUN apt-get update
RUN apt-get install -y ca-certificates
RUN apt-get install -y wget
RUN apt-get install -y git
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-venv
RUN apt-get update --fix-missing
RUN apt-get -y autoremove
RUN apt-get -y clean

RUN pip install --upgrade pip
RUN pip install -U pip setuptools
RUN pip install --upgrade build
RUN pip install --upgrade twine

COPY ./requirements.txt .
RUN pip install -r requirements.txt


# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV PYTHONPATH=/workspace

WORKDIR /workspace
COPY . /workspace

ARG USERNAME=vscode
ARG USER_UID=1000

# Creates a non-root user with an explicit UID
RUN adduser -u $USER_UID --disabled-password --gecos "" $USERNAME
USER $USERNAME

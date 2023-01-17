# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN pip install -U pip setuptools; pip install -U poetry

WORKDIR /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app

# copy pre-required files for dependency installation
COPY scripts ./scripts
COPY pyproject.toml ./
COPY poetry.lock ./
COPY poetry.toml ./
RUN python ./scripts/_docker_poetry_fix.py

# # Creates a non-root user with an explicit UID and adds permission to access the /app folder
USER appuser
# Install pip requirements
RUN poetry install --no-dev --no-cache --without=docs

COPY broker ./
# # For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers

# # During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["bash", "-c", "source .venv/bin/activate; gunicorn --bind 0.0.0.0:5000 routes:app"]

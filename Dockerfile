# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim as poetry

RUN pip install -U pip setuptools && pip install --no-cache-dir -U poetry

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN poetry export --without=dev,docs --output requirements.txt

# == Main image == #
FROM python:3.10-slim
EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN pip install -U pip setuptools

WORKDIR /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app

# Install pip requirements
COPY --from=poetry /app/requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# # Creates a non-root user with an explicit UID and adds permission to access the /app folder
USER appuser

COPY broker ./

# # During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["bash", "-c", "gunicorn --bind 0.0.0.0:5000 routes:app"]

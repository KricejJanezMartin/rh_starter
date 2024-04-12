# The builder image, used to build the virtual environment
FROM python:3.10-buster as builder

RUN pip install poetry==1.7.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

# Add Gunicorn to your dependencies
RUN poetry add gunicorn

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.10-slim-bullseye as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    FLASK_ENV=production

# Set environment variables
ENV DB_HOST=mysql
ENV DB_USER=root
ENV DB_PASSWORD=hcQXGBcDSWAx3N0J
ENV DB_NAME=weather_data

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . /app

WORKDIR /app

EXPOSE 5000

# Use Gunicorn to start your application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

# Build the Docker image
#docker build -f webapp/Dockerfile .

# Tag the image
#docker tag front-weather-app:latest docker.io/janezmk/troia-front-webapp:latest

# Push the image to the Docker registry
#docker push docker.io/janezmk/troia-front-webapp:latest
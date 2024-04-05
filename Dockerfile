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

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.10-slim-bullseye as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
# Set environment variables
ENV DB_HOST=10.217.4.154
ENV DB_USER=root
ENV DB_PASSWORD=hcQXGBcDSWAx3N0J
ENV DB_NAME=weather_data
    

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY src /app/src

WORKDIR /app/src

ENTRYPOINT ["python", "-u", "fetchWeather.py"]


# Build the Docker image
#docker build -t weather-app .

# Tag the image
#docker tag weather-app:latest docker.io/yourusername/weather-app:latest

# Push the image to the Docker registry
#docker push docker.io/yourusername/weather-app:latest

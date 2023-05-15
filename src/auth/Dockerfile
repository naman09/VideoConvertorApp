FROM python:3.10-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential default-libmysqlclient-dev \
    && pip install --no-cache-dir --upgrade pip


WORKDIR /app

# Create a different layer for requirements. So that if there are no changes to dependency docker can reuse the
# exisitng layer
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

# serve as a hint/documentation that on which port container will listen on
EXPOSE 3000

CMD ["python3", "server.py"]


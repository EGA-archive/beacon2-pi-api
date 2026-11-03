
FROM python:3.13.18-slim-bookworm AS builder

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
      g++ ca-certificates curl gnupg \
  && update-ca-certificates -f \
  && rm -rf /var/lib/apt/lists/*

ENV NODE_MAJOR=20
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip before downloading Python packages
RUN python -m pip install --no-cache-dir --upgrade "pip>=26.2.2"

COPY requirements.txt .
RUN python -m pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Install requirements, enforce secure certifi, build assets
RUN python -m pip install --no-cache-dir -r requirements.txt && \
    python -m pip install --no-cache-dir --upgrade \
        "pip>=26.2.2" "certifi>=2026.10.19" && \
    npm run tailwind:build && \
    python manage.py collectstatic --noinput

FROM python:3.13.18-slim-bookworm

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends ca-certificates && \
    update-ca-certificates -f && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/app && \
    addgroup --system app && \
    adduser --system --group app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=prod
ENV TESTING=0
ENV PYTHONPATH=/home/app/web
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt

WORKDIR $APP_HOME

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

RUN python -m pip install --no-cache-dir --no-index /wheels/* && \
    python -m pip install --no-cache-dir --upgrade \
        "pip>=26.2.2" "certifi>=2026.10.19" && \
    rm -rf /wheels

COPY --from=builder /usr/src/app/media $APP_HOME/media
COPY --from=builder /usr/src/app/staticfiles $APP_HOME/staticfiles
COPY . $APP_HOME

RUN chown -R app:app $HOME

USER app

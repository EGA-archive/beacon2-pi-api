FROM python:3.13-slim-bookworm AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        g++ \
        ca-certificates \
        curl \
        gnupg \
    && rm -rf /var/lib/apt/lists/*

ENV NODE_MAJOR=20

RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
        | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" \
        > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip wheel --wheel-dir /wheels -r requirements.txt

RUN pip install --no-cache-dir /wheels/*

COPY package.json package-lock.json ./

RUN npm ci

COPY . .

RUN npm run tailwind:build

RUN python manage.py collectstatic --noinput

FROM python:3.13-slim-bookworm

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system app \
    && adduser --system --group app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web

RUN mkdir -p $APP_HOME

WORKDIR $APP_HOME

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=prod
ENV TESTING=0
ENV PYTHONPATH=$APP_HOME

COPY --from=builder /wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir /wheels/*

COPY --from=builder /usr/src/app $APP_HOME

RUN chown -R app:app $HOME

USER app
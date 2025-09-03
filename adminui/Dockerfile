FROM python:3.13-slim-bookworm as builder

RUN apt-get update \
  && apt-get -y install g++ ca-certificates curl gnupg \
  && apt-get clean

ENV NODE_MAJOR=20
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && apt-get install nodejs -y

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .
RUN pip install --upgrade pip && pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

COPY package.json package-lock.json ./
RUN npm install

RUN pip install -r requirements.txt && npm run tailwind:build && python manage.py collectstatic --noinput

FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get upgrade -y && apt-get clean

RUN mkdir -p /home/app

RUN addgroup --system app && adduser --system --group app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT prod
ENV TESTING 0
ENV PYTHONPATH $APP_HOME

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
COPY --from=builder /usr/src/app/media $APP_HOME/media
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

COPY . $APP_HOME

RUN chown -R app:app $HOME

USER app
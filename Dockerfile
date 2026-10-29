##########################
## Build env
##########################

FROM python:3.13.18-bookworm AS BUILD

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        openssh-client \
        sshpass \
        nginx \
    && update-ca-certificates -f \
    && rm -rf /var/lib/apt/lists/*

# Python packages
RUN python -m pip install --no-cache-dir --upgrade "pip>=26.2.2"

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

# Enforce secure versions after installing requirements
RUN python -m pip install --no-cache-dir --upgrade \
    "pip>=26.2.2" \
    "certifi>=2026.10.19"

##########################
## Final image
##########################
FROM python:3.13.18-bookworm

LABEL maintainer "CRG System Developers"
LABEL org.label-schema.schema-version="2.0"
LABEL org.label-schema.vcs-url="https://github.com/EGA-archive/beacon-2.x/"


ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt

COPY --from=BUILD /usr/local/bin /usr/local/bin
COPY --from=BUILD /usr/local/lib /usr/local/lib

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        openssh-client \
        sshpass \
        nginx \
    && update-ca-certificates -f \
    && rm -rf /var/lib/apt/lists/*

COPY . .

WORKDIR .
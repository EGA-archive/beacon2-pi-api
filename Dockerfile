##########################
## Build env
##########################

FROM python:3.13-bookworm AS BUILD

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
#RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
    ca-certificates pkg-config make \
    libssl-dev libffi-dev libpq-dev \
    && update-ca-certificates -f \

# python packages
RUN pip install --upgrade pip
RUN python -m pip install --upgrade \
    "pip>=26.2.2"
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

##########################
## Final image
##########################
FROM python:3.13-bookworm

LABEL maintainer "CRG System Developers"
LABEL org.label-schema.schema-version="2.0"
LABEL org.label-schema.vcs-url="https://github.com/EGA-archive/beacon-2.x/"

# Too much ?
COPY --from=BUILD /usr/local/bin      /usr/local/bin
COPY --from=BUILD /usr/local/lib      /usr/local/lib

RUN apt-get update && \
    apt update && apt install -y openssh-client sshpass && \
    apt-get install -y --no-install-recommends \
    nginx \
    && \
    rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/nginx.list && \
    apt-get purge -y --auto-remove

COPY . .

WORKDIR .
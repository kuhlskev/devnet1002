# our base image
FROM alpine:3.5
MAINTAINER Kevin Kuhls <kekuhls@cisco.com>

# Install python and pip

RUN apk add --update python2-dev py2-pip openssl-dev libffi-dev musl-dev libxml2-dev libxslt-dev openssh gcc \
    && pip install --upgrade pip \
    && pip install ansible requests xlrd lxml ncclient netaddr \
    && apk del --update gcc \
    && rm -rf /var/cache/apk/* \
    && mkdir -p ~/.ssh \
    && printf "StrictHostKeyChecking no\nHostKeyAlgorithms +ssh-dss\nKexAlgorithm +diffie-hellman-group1-sha1\n" \\
        >> ~/.ssh/config \
    && chmod -R 600 ~/.ssh \
    && touch ~/.ssh/known_hosts

WORKDIR /home/docker
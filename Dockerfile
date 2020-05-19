ARG PYTHON_VERSION=3.7.1-alpine3.7

FROM python:${PYTHON_VERSION} as builder

WORKDIR /usr/src

VOLUME /build
VOLUME /report

COPY ./requires.txt ./
COPY ./scripts/build_jailkit.sh ./scripts/

RUN apk add --no-cache bash ca-certificates \
 && echo http://dl-2.alpinelinux.org/alpine/edge/community/ >> /etc/apk/repositories \
 && apk add --no-cache --virtual build-deps openssl make alpine-sdk shadow \
 && pip install -U pip \
 && pip install coverage \
 && pip install flake8 \
 && pip install pylint \
 && pip install pytest \
 && pip install responses \
 && pip wheel -r ./requires.txt -w /wheels \
 && pip install -r ./requires.txt -f /wheels \
 && ./scripts/build_jailkit.sh \
 && mkdir -p /secrets/ssl/cert \
 && touch /secrets/ssl/cert/.disable_cert_validation

COPY . .

RUN /usr/bin/openssl req -x509 -newkey rsa:2048 -nodes -keyout /secrets/ssl/cert/private_key.pem \
                         -out /secrets/ssl/cert/certificate.pem \
                         -days 365 \
                         -subj "/C=US/ST=Texas/L=Austin/O=Cisco/OU=longhorn/CN=python" \
 && python setup.py bdist_wheel \
 && mv ./dist/template_adapter-1.0-py2.py3-none-any.whl /wheels


##
## Dist stage
##
FROM python:${PYTHON_VERSION} as dist

WORKDIR /root

ENV CERTFILE /secrets/ssl/cert/certificate.pem
ENV PKEYFILE /secrets/ssl/cert/private_key.pem
ENV CAFILE /secrets/ssl/ca/ca_certificate.pem

ENV JAIL_GROUPNAME script_executer
ENV JAIL_USERNAME script_executer
ENV JAIL_DIR /jail

COPY --from=builder /secrets/ /secrets/
COPY --from=builder /etc/jailkit/* /etc/jailkit/
COPY --from=builder /usr/sbin/jk_* /usr/sbin/
COPY --from=builder /usr/bin/jk_* /usr/bin/
COPY --from=builder /usr/share/jailkit/* /usr/share/jailkit/
COPY --from=builder /wheels /wheels
COPY ./scripts/setup_jail.sh /root/setup_jail.sh

RUN apk add --no-cache bash \
 && echo http://dl-2.alpinelinux.org/alpine/edge/community/ >> /etc/apk/repositories \
 && apk add --no-cache shadow \
 && pip install /wheels/template_adapter-1.0-py2.py3-none-any.whl -f /wheels \
 && /root/setup_jail.sh \
 && rm -f /root/setup_jail.sh \
 && rm -rf /wheels \
 && apk del shadow


EXPOSE 8082

ENTRYPOINT ["/usr/local/bin/activities-worker"]


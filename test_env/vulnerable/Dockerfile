FROM alpine:3.15

# DL-02: No USER directive, runs as root
# DL-03: ADD used instead of COPY (even for local files it's flagged as WARN)
ADD dummy.txt /dummy.txt

# DL-04: Exposing SSH port
EXPOSE 22

# DL-05: apk add without --no-cache (or apt-get without --no-install-recommends)
# DL-07: Isolated update instruction
RUN apk update
RUN apk add curl python3

# DL-08: Storing a secret in ENV
ENV API_SECRET_KEY=12345abcdef

# No HEALTHCHECK (DL-06)

CMD ["/bin/sh"]

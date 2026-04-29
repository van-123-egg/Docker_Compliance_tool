# IMG-01, DL-01: Pinned version instead of latest
FROM alpine:3.19.1

# DL-02: Non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# DL-03: Use COPY instead of ADD
COPY . /app

# DL-05, DL-07: Use --no-cache (or equivalent) and chain updates
RUN apk add --no-cache curl

# DL-06: HEALTHCHECK is defined
HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost/ || exit 1

WORKDIR /app
USER appuser

CMD ["/bin/sh"]

FROM python:3.8.15-buster as builder

WORKDIR /app
COPY . .
RUN python3 -m pip install --no-cache-dir --progress-bar off -U pip setuptools wheel && \
    python3 -m pip install --no-cache-dir --progress-bar off .

FROM python:3.8.15-slim-buster

LABEL org.opencontainers.image.authors="National Institute of Informatics, Japan"
LABEL org.opencontainers.image.url="https://github.com/NII-DG/nii-dg"
LABEL org.opencontainers.image.source="https://raw.githubusercontent.com/NII-DG/nii-dg/main/Dockerfile"
LABEL org.opencontainers.image.version="1.0.2"
LABEL org.opencontainers.image.licenses="Apache2.0"

RUN apt update && \
    apt install -y --no-install-recommends \
    tini && \
    apt clean &&\
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages

WORKDIR /app
COPY . .

EXPOSE 5000

ENV DG_HOST 0.0.0.0
ENV DG_PORT 5000
ENV DG_USE_EXTERNAL_CTX False
ENV DG_ALLOW_OTHER_GH_REPO False
ENV DG_WSGI_SERVER waitress
ENV DG_WSGI_THREADS 1

ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["tini", "--"]
CMD ["sleep", "infinity"]

FROM python:3.8.15-buster as builder

WORKDIR /app
COPY . .
RUN python3 -m pip install --no-cache-dir --progress-bar off -U pip setuptools wheel && \
    python3 -m pip install --no-cache-dir --progress-bar off .

FROM python:3.8.15-slim-buster

LABEL org.opencontainers.image.authors="National Institute of Informatics, Japan"
LABEL org.opencontainers.image.url="https://github.com/NII-DG/nii-dg"
LABEL org.opencontainers.image.source="https://raw.githubusercontent.com/NII-DG/nii-dg/main/Dockerfile"

RUN apt update && \
    apt install -y --no-install-recommends \
    tini && \
    apt clean &&\
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages

WORKDIR /app
COPY . .

ENTRYPOINT ["tini", "--"]
CMD ["sleep", "infinity"]
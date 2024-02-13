ARG BENK_ALMALINUX_TAG
FROM --platform=$BUILDPLATFORM public.ecr.aws/docker/library/almalinux:${BENK_ALMALINUX_TAG} AS build
ADD requirements.txt .
RUN dnf install -y python python-pip fio && \
    mkdir /app /output && \
    pip install -r requirements.txt && \
    rm requirements.txt
ADD src/benk /app/benk

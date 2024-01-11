ARG BENK_ALMALINUX_TAG
FROM --platform=$BUILDPLATFORM public.ecr.aws/docker/library/almalinux:${BENK_ALMALINUX_TAG} AS build
#FROM --platform=$BUILDPLATFORM almalinux:${BENK_ALMALINUX_TAG} AS build
ARG BENK_FIO_VERSION
RUN dnf install -y 'dnf-command(config-manager)' && \
    dnf config-manager --set-enabled crb && \
    dnf install -y wget gcc make glibc-static libaio-devel
RUN wget https://github.com/axboe/fio/archive/refs/tags/fio-${BENK_FIO_VERSION}.tar.gz && \
    tar xzvf fio-${BENK_FIO_VERSION}.tar.gz
# FIXME include libaio
RUN cd fio-fio-${BENK_FIO_VERSION} && \
    ./configure --build-static --prefix=/usr/local && \
    make && make install

FROM --platform=$BUILDPLATFORM public.ecr.aws/docker/library/almalinux:${BENK_ALMALINUX_TAG}
#FROM --platform=$BUILDPLATFORM almalinux:${BENK_ALMALINUX_TAG}
ADD requirements.txt .
RUN dnf install -y python python-pip && \
    mkdir /app /output && \
    pip install -r requirements.txt && \
    rm requirements.txt
ADD src/benk /app/benk
COPY --from=build /usr/local/bin/fio /bin/fio

FROM ubuntu:22.04

#RUN groupadd -r appuser && useradd -r -g appuser -m -u 1000 appuser
RUN groupadd -g 1000 appuser && useradd -r -u 1000 -g appuser -s /bin/bash appuser

RUN apt-get update && apt-get install -y \
    pcsc-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/appuser

USER appuser

CMD ["pcsc_scan"]
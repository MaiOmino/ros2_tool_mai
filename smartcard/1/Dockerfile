FROM ubuntu:22.04

#RUN groupadd -r appuser && useradd -r -g appuser -m -u 1000 appuser
RUN groupadd -g 1000 appuser && useradd -r -u 1000 -g appuser -s /bin/bash appuser

RUN apt-get update && apt-get install -y \
    pcscd \
    pcsc-tools \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/pcscd && chown appuser:appuser /var/run/pcscd


WORKDIR /home/appuser

USER appuser

CMD ["pcscd", "-f", "-d", "-s", "/var/run/pcscd"]
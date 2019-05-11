FROM docker.zenterio.lan/library/python:2-stretch

LABEL description="PDF Render Server for Zenterio's Mediawiki installation"

RUN \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        supervisor \
        re2c \
        default-jre-headless \
        pdftk \
        imagemagick \
        texvc \
    && rm -r /var/lib/apt/lists/*

COPY supervisord.conf /etc/supervisord.conf

COPY mwlib-0.16.1.patch mwlib.rl-0.14.6.patch /tmp/

WORKDIR /tmp
RUN \
    # Patch mwlib version 0.16.1
    git clone https://github.com/pediapress/mwlib.git -b 0.16.1 && \
    patch -p1 -i /tmp/mwlib-0.16.1.patch -d mwlib && \
    # Patch mwlib.rl version 0.14.6
    git clone https://github.com/pediapress/mwlib.rl.git -b 0.14.6 && \
    patch -p1 -i /tmp/mwlib.rl-0.14.6.patch -d mwlib.rl && \
    # Install dependencies specified by mwlib
    pip install -r /tmp/mwlib/requirements.txt && \
    # Install mwlib and mwlib.rl from the git checkout
    pip install /tmp/mwlib /tmp/mwlib.rl && \
    # Clean up all checkouts and patch files
    rm -rf mwlib mwlib.rl mwlib-0.16.1.patch mwlib.rl-0.14.6.pathc

# Download plantuml.jar directly into mwlib's install location
WORKDIR /usr/local/lib/python2.7/site-packages/mwlib
RUN \
    curl -L https://sourceforge.net/projects/plantuml/files/1.2018.13/plantuml.1.2018.13.jar/download -o plantuml.jar

WORKDIR /

# Default port for nserve
EXPOSE 80

ENTRYPOINT ["supervisord"]
CMD ["--nodaemon", "--configuration", "/etc/supervisord.conf"]

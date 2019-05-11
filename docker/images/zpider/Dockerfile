FROM docker.zenterio.lan/asciidoctor/docker-asciidoctor:latest

RUN apk add --no-cache \
    imagemagick \
    graphicsmagick \
  && apk add --no-cache --virtual .rubymakedepends \
    build-base \
    libxml2-dev \
    ruby-dev \
    imagemagick-dev \
    graphicsmagick-dev \
  && gem install --no-document \
    minitest \
    prawn-svg \
    prawn-gmagick \
    coderay \
  && apk del -r --no-cache .rubymakedepends

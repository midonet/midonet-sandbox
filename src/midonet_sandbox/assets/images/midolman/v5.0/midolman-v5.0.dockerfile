FROM sandbox/midolman:base
MAINTAINER MidoNet (http://midonet.org)

RUN apt-get install -qy --force-yes \
      midolman \
      midonet-tools

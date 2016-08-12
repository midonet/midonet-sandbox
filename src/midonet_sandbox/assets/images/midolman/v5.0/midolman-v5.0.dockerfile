FROM sandbox/midolman:base
MAINTAINER MidoNet (http://midonet.org)

RUN apt-get install -qy --force-yes --no-install-recommends \
      midolman \
      midonet-tools

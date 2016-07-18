FROM sandbox/midolman:base
MAINTAINER MidoNet (http://midonet.org)

RUN apt-get install -qy \
    midolman \
    midonet-tools

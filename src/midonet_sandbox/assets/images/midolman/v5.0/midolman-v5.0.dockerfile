FROM sandbox/midolman:base
MAINTAINER MidoNet (http://midonet.org)

RUN apt-get install -qy --force-yes midolman=2:5.0.0

FROM sandbox/midolman:base
MAINTAINER MidoNet (http://midonet.org)

RUN apt-get install -qy --force-yes midonet-tools=2:5.0.0 \
                                    midolman=2:5.0.0

FROM sandbox/midolman:base
MAINTAINER MidoNet (http://midonet.org)

ADD bin/run-midolman-host.sh /run-midolman-host.sh
RUN apt-get install -qy --force-yes midonet-tools=2:5.0.1 \
                                    midolman=2:5.0.1

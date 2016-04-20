FROM sandbox/midonet-cluster:base
MAINTAINER MidoNet (http://midonet.org)

RUN apt-get install -qy --force-yes python-midonetclient=2:5.0.1 \
                                    midonet-tools=2:5.0.1 \
                                    midonet-cluster=2:5.0.1

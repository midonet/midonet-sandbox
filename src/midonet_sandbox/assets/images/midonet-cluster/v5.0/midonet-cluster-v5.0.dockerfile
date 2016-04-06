FROM sandbox/midonet-cluster:base
MAINTAINER MidoNet (http://midonet.org)

RUN apt-get install -qy --force-yes python-midonetclient=2:5.0.0 \
                                    midonet-cluster=2:5.0.0

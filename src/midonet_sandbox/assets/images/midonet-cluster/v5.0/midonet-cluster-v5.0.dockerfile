FROM sandbox/midonet-cluster:base
MAINTAINER MidoNet (http://midonet.org)

RUN apt-get install -qy --force-yes \
      midonet-cluster \
      midonet-tools \
      python-midonetclient

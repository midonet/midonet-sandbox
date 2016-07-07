FROM sandbox/midonet-cluster:base
MAINTAINER MidoNet (http://midonet.org)

RUN apt-get install -qy \
      midonet-cluster \
      midonet-tools \
      python-midonetclient

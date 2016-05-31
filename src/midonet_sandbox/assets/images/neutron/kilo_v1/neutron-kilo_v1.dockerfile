FROM sandbox/neutron:kilo
MAINTAINER MidoNet (http://midonet.org)

COPY conf/midonet.ini /etc/neutron/plugins/midonet/midonet.ini
COPY conf/midonetrc /root/.midonetrc

RUN /setup-mariadb.sh

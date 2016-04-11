FROM sandbox/neutron:kilo
MAINTAINER MidoNet (http://midonet.org)

COPY conf/midonet.ini /etc/neutron/plugins/midonet/midonet.ini

# Install the FJ plugin with vpnaas and router peering features
RUN apt-get install -qy --no-install-recommends python-neutron-plugin-midonet-fj

FROM sandbox/neutron:base-xenial
MAINTAINER MidoNet (http://midonet.org)

COPY conf/midonet.ini /etc/neutron/plugins/midonet/midonet.ini

RUN apt-get -q update && DEBIAN_FRONTEND=noninteractive apt-get install -qy ubuntu-cloud-keyring
COPY conf/cloudarchive-ost.list /etc/apt/sources.list.d/cloudarchive-ost.list
RUN apt-get -q update && DEBIAN_FRONTEND=noninteractive apt-get install -qy --no-install-recommends \
                            neutron-server \
                            python-neutronclient \
                            python-keystoneclient \
                            python-midonetclient \
                            python-neutron-lbaas \
                            python-neutron-fwaas \
                            python-neutron-vpnaas \
                            python-setuptools

RUN mv /midonet_conf/neutron-server /etc/default/neutron-server
RUN mv /midonet_conf/neutron_lbaas.conf /etc/neutron/neutron_lbaas.conf
RUN mv /midonet_conf/neutron_vpnaas.conf /etc/neutron/neutron_vpnaas.conf

WORKDIR /
RUN git clone https://github.com/openstack/networking-midonet.git --depth 1 --branch stable/newton && \
    cd /networking-midonet && python setup.py install

RUN /setup-mariadb.sh

FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

COPY conf/midonet.list /etc/apt/sources.list.d/midonet.list
COPY conf/keystonerc /keystonerc
COPY conf/midonetrc /root/.midonetrc
COPY bin/run-neutron.sh /run-neutron.sh

# These files needs to be moved after neutron installation
# Put in a temporary directory so they can be placed correctly on the child image
COPY conf/neutron_defaults /midonet_conf/neutron-server
COPY conf/neutron_lbaas.conf /midonet_conf/neutron_lbaas.conf
COPY conf/neutron_vpnaas.conf /midonet_conf/neutron_vpnaas.conf

RUN apt-get -q update && apt-get install -qy curl
RUN curl -k http://builds.midonet.org/midorepo.key | apt-key add -
RUN apt-get -qy install --no-install-recommends \
                        python-mysql.connector \
                        python-openssl \
                        mariadb-client

CMD ["/run-neutron.sh"]

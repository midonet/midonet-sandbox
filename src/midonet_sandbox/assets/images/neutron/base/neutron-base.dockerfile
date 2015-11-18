FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

COPY conf/midonet.list /etc/apt/sources.list.d/midonet.list
COPY conf/keystonerc /keystonerc
COPY conf/midonetrc /root/.midonetrc
COPY bin/run-neutron.sh /run-neutron.sh

# These files needs to be moved after neutron installation
# Put in a temporary directory so they can be placed correctly on the child image
RUN mkdir /midonet_conf
COPY conf/midonet.ini /midonet_conf/midonet.ini
COPY conf/neutron_lbaas.conf /midonet_conf/neutron_lbaas.conf
COPY conf/neutron_defaults /midonet_conf/neutron-server

RUN apt-get -q update && apt-get install -qy curl
RUN curl -k http://builds.midonet.org/midorepo.key | apt-key add -
RUN apt-get -qy install --no-install-recommends \
                        python-mysql.connector \
                        python-openssl \
                        mariadb-client

ONBUILD COPY conf/cloudarchive-ost.list /etc/apt/sources.list.d/cloudarchive-ost.list
ONBUILD COPY conf/midonet-plugin.list /etc/apt/sources.list.d/midonet-plugin.list

ONBUILD RUN apt-get install -qy ubuntu-cloud-keyring
ONBUILD RUN apt-get -q update
ONBUILD RUN apt-get install -qy --no-install-recommends \
                                neutron-server \
                                python-neutron-lbaas \
                                python-neutronclient \
                                python-keystoneclient \
                                python-neutron-plugin-midonet

ONBUILD RUN mkdir -p /etc/neutron/plugins/midonet
ONBUILD RUN mv /midonet_conf/midonet.ini /etc/neutron/plugins/midonet/midonet.ini
ONBUILD RUN mv /midonet_conf/neutron_lbaas.conf /etc/neutron/neutron_lbaas.conf
ONBUILD RUN mv /midonet_conf/neutron-server /etc/default/neutron-server

#ONBUILD ADD conf/midonet.ini /etc/neutron/plugins/midonet/midonet.ini
#ONBUILD ADD conf/neutron_lbaas.conf /etc/neutron/neutron_lbaas.conf
#ONBUILD ADD conf/neutron_defaults /etc/default/neutron-server

CMD ["/run-neutron.sh"]

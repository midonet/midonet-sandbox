FROM ubuntu:xenial
MAINTAINER MidoNet (http://midonet.org)

ONBUILD RUN apt-get -q update && DEBIAN_FRONTEND=noninteractive apt-get install -qy ubuntu-cloud-keyring
ONBUILD ADD conf/cloudarchive-ost.list /etc/apt/sources.list.d/cloudarchive-ost.list
ONBUILD RUN apt-get -q update
ONBUILD RUN DEBIAN_FRONTEND=noninteractive apt-get -qy dist-upgrade
ONBUILD RUN DEBIAN_FRONTEND=noninteractive apt-get install -qy --no-install-recommends keystone python-openstackclient apache2
ONBUILD RUN sed -i 's/#debug = false/debug = true/' /etc/keystone/keystone.conf

EXPOSE 5000 35357

ADD bin/run-keystone.sh /run-keystone.sh
ADD conf/keystonerc /keystonerc

ENV OS_PROJECT_NAME=admin OS_USERNAME=admin OS_PASSWORD=admin OS_AUTH_URL=http://localhost:5000
ONBUILD RUN keystone-manage db_sync && \
            keystone-manage bootstrap --bootstrap-username admin --bootstrap-password admin \
                                      --bootstrap-project-name admin --bootstrap-role-name admin \
                                      --bootstrap-service-name keystone --bootstrap-region-id RegionOne \
                                      --bootstrap-admin-url http://localhost:35357 --bootstrap-public-url http://localhost:5000 \
                                      --bootstrap-internal-url http://localhost:5000
ONBUILD RUN /usr/sbin/apache2ctl start && \
            openstack role create __member__ && \
            openstack role add --user admin --project admin __member__ && \
            openstack project create service && \
            openstack user create --password neutron neutron && \
            openstack role add --user neutron --project service admin && \
            openstack role add --user neutron --project service __member__ && \
            openstack service create --name neutron network && \
            /usr/sbin/apache2ctl stop

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]

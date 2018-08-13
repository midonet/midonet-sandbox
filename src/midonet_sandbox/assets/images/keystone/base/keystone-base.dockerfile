FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

ONBUILD ADD conf/cloudarchive-ost.list /etc/apt/sources.list.d/cloudarchive-ost.list
ONBUILD RUN apt-mark hold udev
ONBUILD RUN apt-get install -qy ubuntu-cloud-keyring
ONBUILD RUN apt-get -q update && apt-get -qy dist-upgrade
ONBUILD RUN echo "manual" > /etc/init/keystone.override
ONBUILD RUN apt-get install -qy --no-install-recommends keystone python-openstackclient
ONBUILD RUN sed -i 's/#debug = false/debug = true/' /etc/keystone/keystone.conf

EXPOSE 5000 35357

ADD bin/run-keystone.sh /run-keystone.sh
ADD conf/keystonerc /keystonerc
ONBUILD RUN keystone-manage db_sync
CMD ["/run-keystone.sh"]

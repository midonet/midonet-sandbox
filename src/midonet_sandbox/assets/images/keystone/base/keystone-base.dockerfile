FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

ONBUILD ADD conf/cloudarchive-kilo.list /etc/apt/sources.list.d/cloudarchive-kilo.list
ONBUILD RUN apt-get install -qy ubuntu-cloud-keyring
ONBUILD RUN apt-get -q update && apt-get -qy dist-upgrade
ONBUILD RUN echo "manual" > /etc/init/keystone.override
ONBUILD RUN apt-get install -qy keystone python-openstackclient

EXPOSE 5000 35357

ADD bin/run-keystone.sh /run-keystone.sh

CMD ["/run-keystone.sh"]


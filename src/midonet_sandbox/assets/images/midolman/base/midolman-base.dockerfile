FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

ONBUILD ADD conf/midonet.list /etc/apt/sources.list.d/midonet.list
ONBUILD RUN curl -k http://repo.midonet.org/packages.midokura.key | apt-key add -
ONBUILD RUN apt-get -qy update
ONBUILD RUN apt-get install -qqy midolman zkdump

RUN apt-get update && apt-get install -qqy curl

ADD bin/run-midolman.sh /run-midolman.sh
CMD ["/run-midolman.sh"]
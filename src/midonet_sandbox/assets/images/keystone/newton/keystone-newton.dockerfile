FROM sandbox/keystone:base-xenial
MAINTAINER MidoNet (http://midonet.org)

RUN sed -i 's/#admin_token =.*/admin_token = ADMIN/' /etc/keystone/keystone.conf

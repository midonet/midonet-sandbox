FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

COPY conf/midonet.list /etc/apt/sources.list.d/midonet.list
COPY conf/keystonerc /keystonerc
COPY conf/midonetrc /root/.midonetrc
COPY bin/run-neutron.sh /run-neutron.sh
COPY bin/run-neutron-rabbit.sh /run-neutron-rabbit.sh

# These files needs to be moved after neutron installation
# Put in a temporary directory so they can be placed correctly on the child image
COPY conf/neutron_defaults /midonet_conf/neutron-server
COPY conf/neutron_lbaas.conf /midonet_conf/neutron_lbaas.conf
COPY conf/neutron_vpnaas.conf /midonet_conf/neutron_vpnaas.conf

RUN apt-get -q update && apt-get install -qy curl
RUN curl -k http://builds.midonet.org/midorepo.key | apt-key add -
RUN { echo mariadb-server-5 mysql-server/root_password password 'root'; \
      echo mariadb-server-5 mysql-server/root_password_again password 'root'; \
      } | debconf-set-selections
RUN apt-get -qy install --no-install-recommends \
                        python-mysql.connector \
                        python-openssl \
                        mariadb-client \
                        mariadb-server

RUN sed -Ei 's/^(bind-address|log)/#&/' /etc/mysql/my.cnf \
        && echo 'skip-host-cache\nskip-name-resolve\nmax_connections = 2500' | awk '{ print } $1 == "[mysqld]" && c == 0 { c = 1; system("cat") }' /etc/mysql/my.cnf > /tmp/my.cnf \
        && mv /tmp/my.cnf /etc/mysql/my.cnf

COPY bin/setup-mariadb.sh /setup-mariadb.sh

CMD ["/run-neutron.sh"]

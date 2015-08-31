FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

ONBUILD ADD conf/midonet.list /etc/apt/sources.list.d/midonet.list
ONBUILD RUN curl -k http://repo.midonet.org/packages.midokura.key | apt-key add -
ONBUILD RUN apt-get -q update && apt-get install -qqy python-midonetclient
# TODO: install midonet-cluster package from repo once it's published and released

# Add the apt configuration file
RUN apt-get update && apt-get install -qqy curl

# Install Zulu Java 8
RUN apt-get install -qy software-properties-common
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0x219BD9C9
RUN apt-add-repository 'deb http://repos.azulsystems.com/ubuntu stable main'
RUN apt-get update && apt-get install -qy zulu-8

# Configure midonet-cluster
ADD bin/run-midonetcluster.sh /run-midonetcluster.sh
ADD conf/midonetrc /root/.midonetrc

# Expose port for other processes
EXPOSE 8080 8181

# Run midonet-cluster script by default
CMD ["/run-midonetcluter.sh"]

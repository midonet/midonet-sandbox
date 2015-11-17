FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

ONBUILD ADD conf/midonet.list /etc/apt/sources.list.d/midonet.list
ONBUILD RUN curl -k http://repo.midonet.org/packages.midokura.key | apt-key add -
ONBUILD RUN curl -k http://builds.midonet.org/midorepo.key | apt-key add -
ONBUILD RUN apt-get -qy update
ONBUILD RUN apt-get install -qy python-midonetclient midonet-cluster zkdump

# Add the apt configuration file
RUN apt-get update && apt-get install -qqy curl

# Install Java 8
RUN apt-get install -qy software-properties-common
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0x86F44E2A
RUN apt-get update && apt-get install -qy openjdk-8

# Configure midonet-cluster
ADD bin/run-midonetcluster.sh /run-midonetcluster.sh
ADD conf/midonetrc /root/.midonetrc

# Expose port for other processes
EXPOSE 8080 8181

# Run midonet-cluster script by default
CMD ["/run-midonetcluster.sh"]

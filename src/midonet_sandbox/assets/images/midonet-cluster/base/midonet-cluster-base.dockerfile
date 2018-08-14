FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

ONBUILD ADD conf/midonet.list /etc/apt/sources.list.d/midonet.list
ONBUILD RUN curl -k http://artifactory.bcn.midokura.com/artifactory/api/gpg/key/public | apt-key add -
ONBUILD RUN apt-get -qy update
ONBUILD RUN apt-get install -qy python-midonetclient midonet-cluster zkdump

# Add the apt configuration file
RUN apt-get update && apt-get install -qqy curl

# Install Java 8
RUN apt-get install -qy software-properties-common
RUN add-apt-repository -y ppa:openjdk-r/ppa
RUN apt-get update && apt-get install -qy openjdk-8-jdk --no-install-recommends

# Configure midonet-cluster
ADD bin/run-midonetcluster.sh /run-midonetcluster.sh
ADD conf/midonetrc /root/.midonetrc

# Expose port for other processes
EXPOSE 8080 8181

# Run midonet-cluster script by default
CMD ["/run-midonetcluster.sh"]

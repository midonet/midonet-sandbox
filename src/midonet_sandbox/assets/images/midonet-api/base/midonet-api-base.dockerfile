FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

ONBUILD ADD conf/midonet.list /etc/apt/sources.list.d/midonet.list
ONBUILD RUN curl -k http://artifactory.bcn.midokura.com/artifactory/api/gpg/key/public | apt-key add -
ONBUILD RUN apt-get -q update && apt-get install -qqy tomcat7 midonet-api python-midonetclient

# install midolman to get access to mn-conf, but keep the agent itself disabled
ONBUILD RUN apt-get install -qqy midolman
ONBUILD RUN update-rc.d midolman disable

# Add the apt configuration file
RUN apt-get update && apt-get install -qqy curl

# Install Java.
RUN apt-get install -y --no-install-recommends openjdk-7-jre

# Configure midonet-api
ADD conf/midonet-api.xml /etc/tomcat7/Catalina/localhost/midonet-api.xml
RUN mkdir -p /tmp/tomcat7-tomcat7-tmp/
ADD bin/run-midonetapi.sh /run-midonetapi.sh
ADD conf/midonetrc /root/.midonetrc

# Expose port for other processes
EXPOSE 8080 8459 8460

# Run midonet-api script by default
CMD ["/run-midonetapi.sh"]

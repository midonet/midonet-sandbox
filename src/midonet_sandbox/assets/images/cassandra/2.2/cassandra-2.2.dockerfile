FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

# Configure cassandra repos
RUN echo "deb http://debian.datastax.com/community 2.2 main" > /etc/apt/sources.list.d/cassandra.list

RUN apt-get update
RUN apt-get install -qqy curl
RUN curl -L http://debian.datastax.com/debian/repo_key | apt-key add -

RUN apt-get install -qy software-properties-common
RUN add-apt-repository -y ppa:openjdk-r/ppa

RUN apt-get -q update && \
    apt-get install -qqy openjdk-8-jdk-headless dsc22

ADD bin/run-cassandra.sh /run-cassandra.sh

# Expose all cassandra ports
EXPOSE 7000 7001 7199 9042 9160

CMD ["/run-cassandra.sh"]

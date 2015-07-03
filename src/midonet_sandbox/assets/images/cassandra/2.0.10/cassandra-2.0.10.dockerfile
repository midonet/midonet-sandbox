FROM ubuntu:14.04
MAINTAINER MidoNet (http://midonet.org)

# Configure cassandra repos
RUN echo "deb http://debian.datastax.com/community stable main" > /etc/apt/sources.list.d/cassandra.list

RUN apt-get install -qqy curl
RUN curl -L http://debian.datastax.com/debian/repo_key | apt-key add -

RUN apt-get -q update && \
    apt-get install -qqy openjdk-7-jre-headless && \
    apt-get install -qqy dsc20=2.0.10-1 cassandra=2.0.10

ADD bin/run-cassandra.sh /run-cassandra.sh

# Expose all cassandra ports
EXPOSE 7000 7001 7199 9042 9160

CMD ["/run-cassandra.sh"]

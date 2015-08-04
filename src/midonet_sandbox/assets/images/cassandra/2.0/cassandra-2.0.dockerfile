FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

# Configure cassandra repos
RUN echo "deb http://debian.datastax.com/community 2.0 main" > /etc/apt/sources.list.d/cassandra.list

RUN apt-get install -qqy curl
RUN curl -L http://debian.datastax.com/debian/repo_key | apt-key add -

RUN apt-get -q update && \
    apt-get install -qqy openjdk-7-jre-headless && \
    apt-get install -qqy dsc20 && \
    apt-mark hold dsc20 cassandra

ADD bin/run-cassandra.sh /run-cassandra.sh

# Expose all cassandra ports
EXPOSE 7000 7001 7199 9042 9160

CMD ["/run-cassandra.sh"]

FROM ubuntu-upstart:14.04
MAINTAINER Midokura (http://www.midokura.com)

# Configure cassandra repos
RUN echo "deb http://www.apache.org/dist/cassandra/debian 310x main" | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list

RUN apt-get update
RUN apt-get install -qqy curl
RUN curl -L http://debian.datastax.com/debian/repo_key | apt-key add -
RUN curl https://www.apache.org/dist/cassandra/KEYS | sudo apt-key add -
RUN sudo apt-key adv --keyserver pool.sks-keyservers.net --recv-key A278B781FE4B2BDA

RUN apt-get install -qy software-properties-common
RUN add-apt-repository -y ppa:openjdk-r/ppa

RUN apt-get -q update && \
    apt-get install -qqy openjdk-8-jdk-headless cassandra

ADD bin/run-cassandra.sh /run-cassandra.sh

# Expose all cassandra ports
EXPOSE 7000 7001 7199 9042 9160

CMD ["/run-cassandra.sh"]
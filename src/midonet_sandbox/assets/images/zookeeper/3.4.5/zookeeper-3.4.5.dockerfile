FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

# Install zookeeper and dependences
RUN apt-get -q update && \
    apt-get install -qqy zookeeper=3.4.5+dfsg-1 zookeeperd=3.4.5+dfsg-1

ADD bin/run-zookeeper.sh /run-zookeeper.sh
RUN chmod +x /run-zookeeper.sh

# Expose all zookeeper ports
EXPOSE 2181 2888 3888

CMD ["/run-zookeeper.sh"]

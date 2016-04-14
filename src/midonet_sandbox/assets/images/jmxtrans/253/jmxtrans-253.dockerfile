FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

WORKDIR /root

# Make sure the package repository is up to date.
RUN apt-get -qy update
RUN apt-get install -qy openjdk-7-jre curl --no-install-recommends
RUN wget http://central.maven.org/maven2/org/jmxtrans/jmxtrans/253/jmxtrans-253.deb
RUN dpkg -i jmxtrans-253.deb
RUN sed -i 's/JMXTRANS_USER=.*/JMXTRANS_USER=root/' /etc/init.d/jmxtrans
RUN sed -i 's/HEAP_SIZE=.*/HEAP_SIZE=128/' /etc/default/jmxtrans

ADD bin/preprocess_stats /usr/bin/preprocess_stats
ADD bin/prometheize /usr/bin/prometheize
ADD bin/upload_stats /usr/bin/upload_stats

VOLUME ["/data", "/var/lib/jmxtrans"]

CMD ["/sbin/init"]
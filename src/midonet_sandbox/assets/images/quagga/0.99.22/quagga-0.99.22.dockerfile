FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

RUN apt-get -q update && apt-get install -qqy git quagga iptables telnet traceroute ethtool python-scapy

# Get pipework to allow arbitrary configurations on the container from the host
# Might get included into docker-networking in the future
RUN git clone http://github.com/jpetazzo/pipework /pipework
RUN mv /pipework/pipework /usr/bin/pipework

ADD bin/run-quagga.sh /run-quagga.sh

RUN chown quagga.quaggavty -R /etc/quagga

ADD conf/bgpd.conf /etc/quagga/bgpd.conf
ADD conf/zebra.conf /etc/quagga/zebra.conf

EXPOSE 179

CMD ["./run-quagga.sh"]

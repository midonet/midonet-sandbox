FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

ADD conf/root_bashrc /root/.bashrc
ADD bin/create_veth_pair /usr/local/bin/create_veth_pair
ADD bin/upload_mem_stats /usr/local/bin/upload_mem_stats
ONBUILD ADD conf/midonet.list /etc/apt/sources.list.d/midonet.list
ONBUILD ADD bin/run-midolman.sh /run-midolman.sh
ADD bin/run-midolman-host.sh /run-midolman-host.sh
ADD src/fake_snort.c /tmp/fake_snort.c
RUN touch /etc/init.d/vpp

ONBUILD RUN curl -k http://repo.midonet.org/packages.midokura.key | apt-key add -
ONBUILD RUN curl -k http://builds.midonet.org/midorepo.key | apt-key add -
ONBUILD RUN apt-get -qy update
ONBUILD RUN apt-get install -qy --no-install-recommends midolman zkdump python-setproctitle

RUN apt-get -qy update
RUN apt-get -qy install git mz hping3 tcpdump nmap iptables telnet traceroute iputils-arping ethtool python-scapy --no-install-recommends

# Install Java 8
RUN apt-get install -qy software-properties-common
RUN add-apt-repository -y ppa:openjdk-r/ppa
RUN apt-get update && apt-get install -qy openjdk-8-jdk --no-install-recommends

# get deps and compile fake snort
RUN apt-get install -qy libpcap-dev
RUN gcc -o /usr/bin/fake_snort /tmp/fake_snort.c -lpcap

# Get pipework to allow arbitrary configurations on the container from the host
# Might get included into docker-networking in the future
RUN git clone http://github.com/jpetazzo/pipework /pipework
RUN mv /pipework/pipework /usr/bin/pipework

# Workaround to circumvent limitations with AppArmor profiles and docker
RUN mv /usr/sbin/tcpdump /usr/bin/tcpdump
RUN mv /sbin/dhclient /usr/bin/dhclient

RUN apt-get update && apt-get install -qy curl && apt-get install -qy git uuid

# Expose bgpd port in case it's a gateway
EXPOSE 179

CMD ["/run-midolman.sh"]

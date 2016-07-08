FROM gcr.io/google_containers/hyperkube-amd64:v1.2.0
MAINTAINER MidoNet (http://midonet.org)

# MidoNet configuration files
ADD conf/root_bashrc /root/.bashrc
ADD bin/create_veth_pair /usr/local/bin/create_veth_pair
ADD conf/midonet.list /etc/apt/sources.list.d/midonet.list
ADD bin/run_kubernetes.sh /run_kubernetes.sh
ADD conf/debian.list /etc/apt/sources.list.d/debian.list

RUN rm /etc/apt/sources.list

# MidoNet Keys
RUN curl -k http://repo.midonet.org/packages.midokura.key | apt-key add -
RUN curl -k http://builds.midonet.org/midorepo.key | apt-key add -

# Install utilities
RUn apt-get -qy update
RUN apt-get -qy install git mz hping3 tcpdump nmap iptables telnet traceroute --no-install-recommends

# Install Java 8
RUN apt-get install -qy software-properties-common
# RUN add-apt-repository -y ppa:openjdk-r/ppa
RUN apt-get -qy update
RUN apt-get install -qy openjdk-8-jdk --no-install-recommends

# Get pipework to allow arbitrary configurations on the container from the host
# Might get included into docker-networking in the future
RUN git clone http://github.com/jpetazzo/pipework /pipework
RUN mv /pipework/pipework /usr/bin/pipework

# We need to have the CNI driver installed in the kubelet container
RUN apt-get -qy update && apt-get -qy install curl git python3 gcc python3-dev
RUN git clone http://github.com/midonet/kuryr /opt/kuryr -b k8s
RUN cd /opt/kuryr && curl https://bootstrap.pypa.io/get-pip.py | python3 - && pip3 install .
RUN mkdir -p /usr/libexec/kubernetes/kubelet-plugins/net/exec/
COPY conf/kuryr.conf /usr/libexec/kubernetes/kubelet-plugins/net/exec/kuryr.conf
RUN mkdir -p /usr/local/lib/python3.4/dist-packages/usr/libexec/kuryr
RUN cp -r /opt/kuryr/usr/libexec/kuryr/* /usr/local/lib/python3.4/dist-packages/usr/libexec/kuryr/

# We don't need the kube-proxy
RUN rm /etc/kubernetes/manifests/kube-proxy.json

# Install mm-ctl (we only need mm-ctl)
RUN apt-get -qy update
RUN apt-get install -qy wget
RUN apt-get install python-setproctitle
RUN cd apt-get download midolman \
    && mv midolman* /tmp/midolman.deb \
    && dpkg -i \
          --ignore-depends=openvswitch-datapath-dkms,bridge-utils,haproxy,quagga,libreswan,iproute,midonet-tools \
          /tmp/midolman.deb \
    && rm /tmp/midolman.deb

# This step is needed to access to K8s server from the bridged network of the containers
RUN sed -i s/--insecure-bind-address=127.0.0.1/--insecure-bind-address=0.0.0.0/ /etc/kubernetes/manifests/master.json

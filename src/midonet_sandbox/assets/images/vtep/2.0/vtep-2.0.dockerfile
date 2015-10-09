FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

WORKDIR /root

# Make sure the package repository is up to date.
RUN apt-get update

# Install add-apt-repository and syslogd
RUN apt-get install -y software-properties-common

# Setup mighost repository for ovenvswitch-vtep
# (with workaround for mighost supporting saucy and not trusty)
RUN add-apt-repository ppa:mighost/ppa
RUN echo "deb http://ppa.launchpad.net/mighost/ppa/ubuntu saucy main" > /etc/apt/sources.list.d/mighost-ppa-trusty.list
RUN apt-get update

# Install OpenVSwitch 2.0
RUN apt-get install -y openvswitch-common openvswitch-switch openvswitch-vtep

# Configure openvswitch to start vtep
RUN cp /etc/default/openvswitch-vtep /etc/default/openvswitch-vtep.orig
RUN grep -v -e '^[[:blank:]]*ENABLE_OVS_VTEP[[:blank:]]*=' /etc/default/openvswitch-vtep.orig > /etc/default/openvswitch-vtep
RUN echo 'ENABLE_OVS_VTEP="true"' >> /etc/default/openvswitch-vtep

# Hack the openvswitch start script to enable management port 6632
RUN grep -q -e '--remote=ptcp:6632' /etc/init.d/openvswitch-vtep || sed -i.orig -e 's/^\([[:blank:]]*\)\(--remote=db:hardware_vtep.*\)/\1\2\n\1--remote=ptcp:6632 \\/' /etc/init.d/openvswitch-vtep

# Stop openvswitch to make sure everything is stable
RUN /etc/init.d/openvswitch-vtep stop

# Add initialization and configuration scripts
ADD bin/run-vtep.sh /run-vtep.sh
ADD bin/configure-vtep.sh /configure-vtep.sh
RUN chmod a+rx /run-vtep.sh
RUN chmod a+rx /configure-vtep.sh

# Expose VTEP management port
EXPOSE 6632

# Expose VTEP tunnel port
EXPOSE 4789

CMD ["/run-vtep.sh"]

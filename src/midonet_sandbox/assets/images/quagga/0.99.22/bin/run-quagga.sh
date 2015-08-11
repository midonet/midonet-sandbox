#!/bin/bash

# Wait for configured interfaces to be set up
# The name of each additional interface should be provided
# in an env var with the _IFACE suffix.
for IFACE in `env | grep -Ev "MIDOLMAN" | grep _IFACE | cut -d= -f2`; do
    # TODO: change pipework by native docker networking once stable
    echo "Waiting for interface $IFACE to be up through pipework"
        timeout 60s pipework --wait -i $IFACE
        if [ $? -eq 124 ]; then
            echo "Interface $IFACE was not ready after 60s. Exiting..."
            exit 1
        fi
done

chown quagga.quaggavty /etc/quagga/*

sed -i -e 's/zebra=no/zebra=yes/' -e 's/bgpd=no/bgpd=yes/' /etc/quagga/daemons

# Pick the IPs and ASs of the peering midolman through links
# Rewrite bgpd.conf to point to peering midolmans
for BGP_PEER in `env | grep MIDOLMAN | grep BGP | grep IP_AS | cut -d= -f2 | sort -u`; do
  IP_PEER=$(echo $BGP_PEER | cut -d: -f1)
  AS_PEER=$(echo $BGP_PEER | cut -d: -f2)
  echo "    neighbor $IP_PEER remote-as $AS_PEER" >> /etc/quagga/bgpd.conf
  echo "    neighbor $IP_PEER timers 1 3" >> /etc/quagga/bgpd.conf
  echo "    neighbor $IP_PEER timers connect 1" >> /etc/quagga/bgpd.conf
done

# Pick the AS of this quagga instance
if [ -z $BGP_AS ]; then
    echo "No BGP AS number specified for this quagga instance."
    echo "Specify it in your yaml flavor description as an environment variable. eg:"
    echo "environment:"
    echo "- BGP_AS=64512"
    exit 1
fi

sed -i "s/router bgp 64512/router bgp $BGP_AS/" /etc/quagga/bgpd.conf

# Set 1.1.1.1/32 to the lo interface to emulate internet access
ip addr add 1.1.1.1/32 dev lo

echo Starting Quagga...
exec /sbin/init

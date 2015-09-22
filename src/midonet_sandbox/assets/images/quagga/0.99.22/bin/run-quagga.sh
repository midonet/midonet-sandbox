#!/bin/bash

# Wait for configured interfaces to be set up
# The name of each additional interface should be provided
# in an env var with the _IFACE suffix.
for IFACE in `env | grep -Ev "ENV" | grep _IFACE | cut -d= -f2 | sort -u`; do
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

# Pick the router-id of this quagga daemon
if [ -z $BGP_ROUTER_ID ]; then
    echo "No router-id specified, using the default 10.0.255.255"
    BGP_ROUTER_ID=10.0.255.255
fi

# Pick the IPs and ASs of the peering midolman and other quaggas through links
# or environment variables. Rewrite bgpd.conf to point to peering midolmans
for BGP_PEER in `env | grep -E "BGPPEER|MIDOLMAN" | grep IP_AS | cut -d= -f2 | sort -u`; do
  IP_PEER=$(echo $BGP_PEER | cut -d: -f1)
  AS_PEER=$(echo $BGP_PEER | cut -d: -f2)
  echo "    neighbor $IP_PEER remote-as $AS_PEER" >> /etc/quagga/bgpd.conf
  echo "    neighbor $IP_PEER timers 1 3" >> /etc/quagga/bgpd.conf
  echo "    neighbor $IP_PEER timers connect 1" >> /etc/quagga/bgpd.conf
  echo "    neighbor $IP_PEER next-hop-self" >> /etc/quagga/bgpd.conf
done

# Pick the AS of this quagga instance
if [ -z "$BGP_AS" ]; then
    echo "No BGP AS number specified for this quagga instance."
    echo "Specify it in your yaml flavor description as an environment variable. eg:"
    echo "environment:"
    echo "- BGP_AS=64512"
    exit 1
fi

# Write advertised networks on bgpd config file if specified
for NETWORK in `env | grep ADVERTISED_NETWORK | cut -d= -f2`; do
    echo "    network $NETWORK" >> /etc/quagga/bgpd.conf
    # Set the network to the lo interface to emulate internet access
    ip addr add $NETWORK dev lo
done

# Set max paths if defined
if [ -n "$BGP_MAX_PATHS" ]; then
    echo "Setting max_paths to $BGP_MAX_PATHS"
    sed -i "s/maximum-paths 2/maximum-paths $BGP_MAX_PATHS/" /etc/quagga/bgpd.conf
fi

# Setting env vars in bgpd config file
sed -i "s/bgp router-id 10.255.255.255/bgp router-id $BGP_ROUTER_ID/" /etc/quagga/bgpd.conf
sed -i "s/router bgp 64512/router bgp $BGP_AS/" /etc/quagga/bgpd.conf

echo Starting Quagga...
exec /sbin/init

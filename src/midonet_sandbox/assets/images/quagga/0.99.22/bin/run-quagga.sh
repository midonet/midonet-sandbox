#!/bin/bash
set -e

FILE=/etc/quagga/bgpd.conf

# Use defaults
BGP_ROUTER_ID=${BGP_ROUTER_ID:-10.0.255.255}
BGP_ADVERTISE_DEFAULT_NETWORK=${BGP_ADVERTISE_DEFAULT_NETWORK:-yes}
BGP_SCAN_TIME=${BGP_SCAN_TIME:-5}
BGP_NEIGHBOR_ADVERTISEMENT_INTERVAL=${BGP_NEIGHBOR_ADVERTISEMENT_INTERVAL:=1}
BGP_ONLY_ADVERTISE_LOCAL=${BGP_ONLY_ADVERTISE_LOCAL:-no}
# Echo parameters' value
set | grep "^BGP"

if [ -z $BGP_AS ]; then
    echo "No BGP AS number specified for this quagga instance."
    echo "Specify it in your yaml flavor as an environment variable. eg:"
    echo "environment:"
    echo "- BGP_AS=64512"
    exit 1
fi

function add_to_neighbor()
{
    echo "    neighbor $1 $2" >> $FILE
}

function add_neighbors()
{
    # Pick the IPs and ASs of the peering midolman and other quaggas through
    # links or environment variables. Rewrite bgpd.conf to point to peering
    # midolmans
    for PEER in `env | grep "BGPPEER" | grep IP_AS | cut -d= -f2 | sort -u`; do
        IP=$(echo $PEER | cut -d: -f1)
        AS=$(echo $PEER | cut -d: -f2)
        add_to_neighbor $IP "remote-as $AS"
        add_to_neighbor $IP "timers 1 3"
        add_to_neighbor $IP "timers connect 3"
        add_to_neighbor $IP \
               "advertisement-interval $BGP_NEIGHBOR_ADVERTISEMENT_INTERVAL"
        add_to_neighbor $IP "next-hop-self"
        if [ "$BGP_ONLY_ADVERTISE_LOCAL" == "yes" ]; then
            add_to_neighbor $IP "filter-list access-list-local out"
        fi
    done
}

echo Wait for configured interfaces to be set up ...
# The name of each additional interface should be provided
# in an env var with the _IFACE suffix.
for IFACE in `env | grep -Ev "ENV" | grep _IFACE | cut -d= -f2 | sort -u`; do
    # TODO: change pipework by native docker networking once stable
    echo "Waiting for interface $IFACE to be up through pipework"
        timeout 300s pipework --wait -i $IFACE
        if [ $? -eq 124 ]; then
            echo "Interface $IFACE was not ready after 60s. Exiting..."
            exit 1
        fi
done

export VTYSH_PAGER=less
echo "export VTYSH_PAGER=less" >> /etc/bash.bashrc

sed -i -e 's/zebra=no/zebra=yes/' -e 's/bgpd=no/bgpd=yes/' /etc/quagga/daemons

echo Modifying daemon configuration file $FILE ...
add_neighbors
# Write advertised networks on bgpd config file if specified
for NETWORK in `env | grep ADVERTISED_NETWORK | cut -d= -f2`; do
    echo "    network $NETWORK" >> $FILE
    if [ "$BGP_ADVERTISE_DEFAULT_NETWORK" == "yes" ]; then
        echo "    network 0.0.0.0/0" >> $FILE
    fi
    # Set the network to the lo interface to emulate internet access
    ip addr add $NETWORK dev lo
done
# Set max paths if defined
if [ -n "$BGP_MAX_PATHS" ]; then
    echo "Setting max_paths to $BGP_MAX_PATHS"
    sed -i "s/maximum-paths 2/maximum-paths $BGP_MAX_PATHS/" $FILE
fi
# Define access list used to filter relay of non-local routes
if [ "$BGP_ONLY_ADVERTISE_LOCAL" == "yes" ]; then
  echo 'ip as-path access-list access-list-local permit ^$' >> $FILE
fi
# Setting env vars in bgpd config file
sed -i "s/bgp router-id 10.255.255.255/bgp router-id $BGP_ROUTER_ID/" $FILE
sed -i "s/router bgp 64512/router bgp $BGP_AS/" $FILE
sed -i "s/bgp scan-time *[0-9]*/bgp scan-time $BGP_SCAN_TIME/" $FILE

echo Starting Quagga...
exec /sbin/init

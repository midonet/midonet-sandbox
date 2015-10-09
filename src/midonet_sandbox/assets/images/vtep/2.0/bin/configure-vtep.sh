#!/bin/bash

# Local IP (as seen from inside the docker)
IP=${LISTEN_ADDRESS:-`hostname --ip-address`}

# If the number of physical ports is not set, default to 4.
if [ -z "$VTEP_PORTS" ]; then
    VTEP_PORTS=4
fi

# If the host subnet is not set, default to 10.0.2.0/24.
if [ -z "$VTEP_HOST_SUBNET" ]; then
    VTEP_HOST_SUBNET="10.0.2.0"
fi

IP_PREFIX=$(echo "$VTEP_HOST_SUBNET" | cut -f 1-3 -d .)
IP_HOST=$(echo "$VTEP_HOST_SUBNET" | cut -f 4 -d .)

# If the management IP is not set, default to the local IP.
if [ -z "$VTEP_MGMT" ]; then
    VTEP_MGMT=$IP
fi

# If the tunnel IP is not set, default to the local IP.
if [ -z "$VTEP_TUNNEL" ]; then
    VTEP_TUNNEL=$IP
fi

if [ "$VTEP_MGMT" != "$VTEP_TUNNEL" ]; then
    if [ ! -d "/sys/devices/virtual/net/eth1" ]; then
        echo "eth1 interface required for different mgmt and tunnel ips"
        echo "waiting for eth1 to appear"
        COUNTDOWN=300
        while [ $COUNTDOWN -gt 0 ]; do
            [ -d "/sys/devices/virtual/net/eth1" ] && break
            sleep 1
            COUNTDOWN=$(($COUNTDOWN - 1))
        done
        if [ ! -d /sys/devices/virtual/net/eth1 ]; then
            echo "timed out"
            exit 1
        fi
        echo "eth1 ready"
    fi
fi

echo "Setting up the VTEP emulator..."
echo "  -> management IP: $VTEP_MGMT"
echo "  -> tunnel IP:     $VTEP_TUNNEL"
echo "  -> host subnet:   $VTEP_HOST_SUBNET"

# Create the physical switch, physical ports and assign the VTEP addresses.
vtep-ctl add-ps vtep0
for i in $(seq 1 $VTEP_PORTS); do
    vtep-ctl add-port vtep0 "swp${i}"
done
vtep-ctl set Physical_Switch vtep0 management_ips=$VTEP_MGMT
vtep-ctl set Physical_Switch vtep0 tunnel_ips=$VTEP_TUNNEL

# Configure the corresponding OVSD bridge.
ovs-vsctl add-br vtep0
for i in $(seq 1 $VTEP_PORTS); do
    ovs-vsctl add-port vtep0 "swp${i}"
done

# Create namespaces representing the hosts behind the VTEP physical ports.
for i in $(seq 1 $VTEP_PORTS); do
    NS="ns${i}"
    PIF="swp${i}"
    VIF="vif${i}"
    HOST_IP="${IP_PREFIX}.$(($IP_HOST + $i))/24"

    echo "Setting up physical port $PIF <-> $VIF : $HOST_IP ($NS)"

    ip netns add $NS
    ip link add $PIF type veth peer name $VIF
    ip link set $VIF netns $NS
    ifconfig $PIF up
    ip netns exec $NS ifconfig lo up
    ip netns exec $NS ifconfig $VIF $HOST_IP up
done

# Restart the VTEP emulator to make sure that configuration is updated.
echo "Restarting the VTEP emulator..."
/etc/init.d/openvswitch-vtep restart

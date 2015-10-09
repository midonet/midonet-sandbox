#!/bin/bash

# The following env variables can be set to change the behavior
# VTEP_PORTS - the number of physical VTEP ports
# VTEP_HOST_SUBNET - the IP subnet used for the hosts connected to the VTEP
#                    ports

#
# Sanity check: openvswitch module must be loaded in the kernel
#
modprobe openvswitch
lsmod | grep -q -w openvswitch
if [ $? -ne 0 ]; then
    echo "OpenVSwitch kernel module is not loaded!"
    exit 1
fi

exec /sbin/init

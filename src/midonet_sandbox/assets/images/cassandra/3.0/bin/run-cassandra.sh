#!/bin/bash

# Parse the IP address of the container
IP=${LISTEN_ADDRESS:-`hostname --ip-address`}

# Get the seeds from an env variable
SEEDS=${SEEDS:-$IP}

# If this container is linked to other cassandra nodes, use them as seeds too
if [[ `env | grep _PORT_9042_TCP_ADDR` ]]; then
    SEEDS="$SEEDS,$(env | grep _PORT_9042_TCP_ADDR | sed 's/.*_PORT_9042_TCP_ADDR=//g' | sed -e :a -e N | sort -u)"
fi

sed -i -e "s/^cluster_name:.*/cluster_name: 'insights-cloud'/
           s/^listen_address:.*$/listen_address: $IP/
           s/rpc_address:.*/rpc_address: $IP/
           s/seeds:.*$/seeds: \"$SEEDS\"/" /etc/cassandra/cassandra.yaml

# Reduce the max_heap_size so it fits on an all-in-one
sed -i -e "s/^#MAX_HEAP_SIZE=.*/MAX_HEAP_SIZE=\"128M\"/
           s/^#HEAP_NEWSIZE=.*/HEAP_NEWSIZE=\"64M\"/" /etc/cassandra/cassandra-env.sh

echo Starting Cassandra on $IP...
exec /sbin/init

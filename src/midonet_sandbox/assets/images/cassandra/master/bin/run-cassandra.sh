#!/bin/bash

# keep cassandra in-memory for performance
mount -t tmpfs -o size=50m tmpfs /var/lib/cassandra
chown -R cassandra.cassandra /var/lib/cassandra

# Parse the IP address of the container
IP=${LISTEN_ADDRESS:-`hostname --ip-address`}

# Get the seeds from an env variable
SEEDS=${SEEDS:-$IP}

# If this container is linked to other cassandra nodes, use them as seeds too
if [[ `env | grep _PORT_9042_TCP_ADDR` ]]; then
    SEEDS="$SEEDS,$(env | grep _PORT_9042_TCP_ADDR | sed 's/.*_PORT_9042_TCP_ADDR=//g' | sed -e :a -e N)"
fi

sed -i -e "s/^cluster_name:.*/cluster_name: 'midonet'/
           s/^listen_address:.*$/listen_address: $IP/
           s/rpc_address:.*/rpc_address: $IP/
           s/seeds:.*$/seeds: \"$SEEDS\"/" /etc/cassandra/cassandra.yaml

echo Starting Cassandra on $IP...
exec cassandra -f

#!/bin/bash

mkdir -p /var/lib/zookeeper

# keep zookeeper in-memory for performance unless is set to false
if [ "${ZOO_IN_MEM}" != "false" ]; then
    mount -t tmpfs -o size=1024m tmpfs /var/lib/zookeeper
fi
# Parse the IP address of the container
LOCAL_ZK_HOST=${LISTEN_ADDRESS:-`hostname --ip-address`}

LOCAL_ZK_ID=$(echo $LOCAL_ZK_HOST | cut -d. -f4)

echo "$LOCAL_ZK_ID" > /var/lib/zookeeper/myid
echo "$LOCAL_ZK_ID" > /etc/zookeeper/conf/myid

# Check if this is the last zookeeper and
# should update linked hosts in conf

# Remove stale configuration (in case of stopped/starded container)
if [ -f /zoo/conf/zoo.cfg ]; then
    rm /zoo/conf/zoo.cfg
fi

# If this ZK container is the one linking to the others, it's in charge
# of updating the shared configuration file. So be it.
if [[ `env | grep _PORT_2888_TCP_ADDR` ]]; then
    MIDO_ZOOKEEPER_HOSTS="$(env | grep _PORT_2888_TCP_ADDR | sed -e 's/.*_PORT_2888_TCP_ADDR=//g' | sort -u)"
    for ZK_HOST in $MIDO_ZOOKEEPER_HOSTS; do
        ZK_ID=$(echo $ZK_HOST | cut -d. -f4)
        echo "server.$ZK_ID=$ZK_HOST:2888:3888" >> /tmp/zoo.cfg
    done
    echo "server.$LOCAL_ZK_ID=$LOCAL_ZK_HOST:2888:3888" >> /tmp/zoo.cfg
    cat /tmp/zoo.cfg >> /zoo/conf/zoo.cfg
fi

# The rest of ZK containers will wait for this file to exist.
echo 'Waiting for config file to appear...'
while [ ! -f /zoo/conf/zoo.cfg ] ; do
    sleep 1
done
echo 'Config file found, starting server.'

cat /zoo/conf/zoo.cfg >> /etc/zookeeper/conf/zoo.cfg
echo "forceSync=no" >> /etc/zookeeper/conf/zoo.cfg

echo "Servers in the QUORUM:"
cat /etc/zookeeper/conf/zoo.cfg

exec /sbin/init

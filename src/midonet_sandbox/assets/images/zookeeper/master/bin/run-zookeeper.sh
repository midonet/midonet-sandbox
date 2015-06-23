#!/bin/bash

if [ -z ${ZOO_ID} ] ; then
    echo 'No ID specified, please specify one between 1 and 255'
    exit -1
fi

mkdir -p /var/lib/zookeeper

# keep zookeeper in-memory for performance
mount -t tmpfs -o size=50m tmpfs /var/lib/zookeeper

# Parse the IP address of the container
IP=${LISTEN_ADDRESS:-`hostname --ip-address`}

echo "${ZOO_ID}" > /var/lib/zookeeper/myid

# Check if this is the last zookeeper and
# should update linked hosts in conf
if [[ `env | grep _PORT_2888_TCP_ADDR` ]]; then
    MIDO_ZOOKEEPER_HOSTS="$(env | grep _PORT_2888_TCP_ADDR | sed -e 's/.*_PORT_2888_TCP_ADDR=//g')"
    for ZK_HOST in $MIDO_ZOOKEEPER_HOSTS; do
        n=$((++n)) && echo "server.$n=$ZK_HOST:2888:3888" >> /tmp/zoo.cfg
    done
    n=$((++n)) && echo "server.$n=$IP:2888:3888" >> /tmp/zoo.cfg
    cat /tmp/zoo.cfg >> /zoo/conf/zoo.cfg
fi

if [ ! -f /conf/zoo.cfg ] ; then
    echo 'Waiting for config file to appear...'
    while [ ! -f /zoo/conf/zoo.cfg ] ; do
        sleep 1
    done
    echo 'Config file found, starting server.'
fi

cat /zoo/conf/zoo.cfg >> /etc/zookeeper/conf/zoo.cfg
echo "Servers in the QUORUM:"
cat /etc/zookeeper/conf/zoo.cfg
/usr/share/zookeeper/bin/zkServer.sh start-foreground

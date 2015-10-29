#!/bin/bash

# Update ZK hosts in case they were linked to this container
if [[ `env | grep _PORT_2181_TCP_ADDR` ]]; then
    ZK_HOSTS="$(env | grep _PORT_2181_TCP_ADDR | sed -e 's/.*_PORT_2181_TCP_ADDR=//g' -e 's/^.*/&:2181/g' | sort -u)"
    ZK_HOSTS="$(echo $ZK_HOSTS | sed 's/ /,/g')"
fi

IP=${LISTEN_ADDRESS:-`hostname --ip-address`}

if [ -z "$ZK_HOSTS" ]; then
    echo "No Zookeeper hosts specified neither by ENV VAR nor by linked containers"
    exit 1
fi

# Update config file to point to ZK
CLUSTER_ENV=/usr/share/midonet-cluster/midonet-cluster-env.sh
MIDO_CFG=`cat $CLUSTER_ENV | grep "MIDO_CFG" | grep -v "MIDO_CFG_FILE" | tr -d '[[:space:]]' | cut -d= -f2`
MIDO_CFG_FILE=`cat $CLUSTER_ENV | grep "MIDO_CFG_FILE" | tr -d '[[:space:]]' | cut -d= -f2`

sed -i -e 's/zookeeper_hosts = .*$/zookeeper_hosts = '"$ZK_HOSTS"'/' $MIDO_CFG/$MIDO_CFG_FILE

# Update cluster logs to report DEBUG
sed -i 's/<root level="INFO">/<root level="DEBUG">/' /etc/midonet-cluster/logback.xml

# Run cluster
exec /sbin/init

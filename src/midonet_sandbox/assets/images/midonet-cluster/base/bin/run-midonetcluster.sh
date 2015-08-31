#!/bin/bash

# Update ZK hosts in case they were linked to this container
if [[ `env | grep _PORT_2181_TCP_ADDR` ]]; then
    ZK_HOSTS="$(env | grep _PORT_2181_TCP_ADDR | sed -e 's/.*_PORT_2181_TCP_ADDR=//g' -e 's/^.*/&:2181/g' | sort -u)"
    ZK_HOSTS="$(echo $ZK_HOSTS | sed 's/ /,/g')"
fi

ZK_ROOT_KEY=/midonet/v1

IP=${LISTEN_ADDRESS:-`hostname --ip-address`}

if [ -z "$ZK_HOSTS" ]; then
    echo "No Zookeeper hosts specified neither by ENV VAR nor by linked containers"
    exit 1
fi

# Edit web.xml
cp /etc/midonet-cluster/logback.xml.dev /etc/midonet-cluster/logback.xml

# Update config file to point to ZK
sed -i -e 's/zookeeper_hosts = .*$/zookeeper_hosts = '"$ZK_HOSTS"'/' /etc/midonet-cluster/midonet-cluster.conf
sed -i -e 's/root_key = .*$/root_key = '"$(echo $ZK_ROOT_KEY|sed 's/\//\\\//g')"'/' /etc/midonet-cluster/midonet-cluster.conf

# Run cluster
exec /sbin/init

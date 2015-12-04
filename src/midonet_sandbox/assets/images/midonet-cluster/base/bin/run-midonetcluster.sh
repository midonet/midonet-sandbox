#!/bin/bash

# Update ZK hosts in case they were linked to this container
if [[ `env | grep _PORT_2181_TCP_ADDR` ]]; then
    ZK_HOSTS="$(env | grep _PORT_2181_TCP_ADDR | sed -e 's/.*_PORT_2181_TCP_ADDR=//g' -e 's/^.*/&:2181/g' | sort -u)"
    ZK_HOSTS="$(echo $ZK_HOSTS | sed 's/ /,/g')"
fi

# Get the linked keystone host
if [[ `env | grep _PORT_35357_TCP_ADDR` ]]; then
    KEYSTONE_HOST=$(env | grep _PORT_35357_TCP_ADDR | cut -d'=' -f2 | sort -u)
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

echo "Setting up basic conf for cluster..."
mn-conf set -t default <<EOF
zookeeper.zookeeper_hosts="$ZK_HOSTS"
EOF

if [ -n "$KEYSTONE_HOST" ]; then
    echo "Setting up keystone because a keystone container was linked"
    mn-conf set -t default <<EOF
    cluster.auth.provider_class="org.midonet.cluster.auth.keystone.v2_0.KeystoneService"
    cluster.auth.admin_role="admin"
    cluster.auth.keystone.tenant_name="admin"
    cluster.auth.keystone.admin_token="ADMIN"
    cluster.auth.keystone.host=$KEYSTONE_HOST
    cluster.auth.keystone.port=35357
EOF
else
    echo "Using MockAuth provider instead of keystone as no container was linked."
fi

echo "Starting cluster!"

# Run cluster
exec /sbin/init

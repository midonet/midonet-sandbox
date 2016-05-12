#!/bin/bash

# RATIONALE: This script do the same as 'run-midolman.sh' but is intended
# to run only when the midolman container runs at the host namespace, not
# in his own.

# Wait for configured interfaces to be set up
# The name of each additional interface should be provided
# in an env var with the _IFACE suffix.

# Default mido_zookeeper_key
if [ -z "$MIDO_ZOOKEEPER_ROOT_KEY" ]; then
    MIDO_ZOOKEEPER_ROOT_KEY=/midonet/v1
fi

# The rest of ZK containers will wait for this file to exist.
echo 'Waiting for config file to appear...'
while [ ! -f /zoo/conf/zoo.cfg ] ; do
    sleep 1
done

echo 'Waiting for midonet_host_id file to appear...'
while [ ! -f /etc/sandbox/midonet_host_id.properties ] ; do
    sleep 1
done

echo 'Config file found, starting server.'

MIDO_ZOOKEEPER_HOSTS=''
for ip in $(grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' /zoo/conf/zoo.cfg);
do
      MIDO_ZOOKEEPER_HOSTS=${MIDO_ZOOKEEPER_HOSTS}${ip}:2181,;
done

# Remove the last ','
MIDO_ZOOKEEPER_HOSTS=${MIDO_ZOOKEEPER_HOSTS::-1}

echo "Configuring agent using MIDO_ZOOKEEPER_HOSTS: $MIDO_ZOOKEEPER_HOSTS"
echo "Configuring agent using MIDO_ZOOKEEPER_ROOT_KEY: $MIDO_ZOOKEEPER_ROOT_KEY"

sed -i -e 's/zookeeper_hosts = .*$/zookeeper_hosts = '"$MIDO_ZOOKEEPER_HOSTS"'/' /etc/midolman/midolman.conf
sed -i -e 's/root_key = .*$/root_key = '"$(echo $MIDO_ZOOKEEPER_ROOT_KEY|sed 's/\//\\\//g')"'/' /etc/midolman/midolman.conf

cp /etc/sandbox/midonet_host_id.properties /etc/midonet_host_id.properties

/hyperkube kubelet --network-plugin=cni --hostname-override='127.0.0.1' --address='0.0.0.0' --api-servers=http://localhost:8080 --cluster-dns=10.0.0.10 --cluster-domain=cluster.local --config=/etc/kubernetes/manifests --allow-privileged=true --v=2

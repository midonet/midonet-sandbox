#!/bin/bash

# RATIONALE: This script does the same as 'run-midolman.sh' but is intended
# to run only when the midolman container runs at the host namespace, not
# in his own.

# Wait for configured interfaces to be set up
# The name of each additional interface should be provided
# in an env var with the _IFACE suffix.
for IFACE in `env | grep _IFACE | cut -d= -f2`; do
    # TODO: change pipework by native docker networking once stable
    echo "Waiting for interface $IFACE to be up"
    timeout 300s pipework --wait -i $IFACE
    if [ $? -eq 124 ]; then
        echo "Interface $IFACE was not ready after 60s. Exiting..."
        exit 1
    fi
done

# Midonet do not support ipv6
sysctl -w net.ipv6.conf.all.disable_ipv6=1
sysctl -w net.ipv6.conf.default.disable_ipv6=1
sysctl -w net.ipv6.conf.lo.disable_ipv6=1

# Default cassandra replication factor
if [ -z "$CASS_FACTOR" ]; then
    CASS_FACTOR=3
fi

# Default mido_zookeeper_key
if [ -z "$MIDO_ZOOKEEPER_ROOT_KEY" ]; then
    MIDO_ZOOKEEPER_ROOT_KEY=/midonet/v1
fi

# The rest of ZK containers will wait for this file to exist.
echo 'Waiting for config file to appear...'
while [ ! -f /zoo/conf/zoo.cfg ] ; do
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

# # Discover the Cassandra services using nmap (TODO(jaume): later on)

echo "Configuring agent using MIDO_ZOOKEEPER_HOSTS: $MIDO_ZOOKEEPER_HOSTS"
echo "Configuring agent using MIDO_ZOOKEEPER_ROOT_KEY: $MIDO_ZOOKEEPER_ROOT_KEY"

mkdir -p /etc/sandbox/
echo "host_uuid=$(uuid)" > /etc/sandbox/midonet_host_id.properties
cp /etc/sandbox/midonet_host_id.properties /etc/midonet_host_id.properties

sed -i -e 's/zookeeper_hosts = .*$/zookeeper_hosts = '"$MIDO_ZOOKEEPER_HOSTS"'/' /etc/midolman/midolman.conf
sed -i -e 's/root_key = .*$/root_key = '"$(echo $MIDO_ZOOKEEPER_ROOT_KEY|sed 's/\//\\\//g')"'/' /etc/midolman/midolman.conf

cat << EOF > /root/.midonetrc
[zookeeper]
zookeeper_hosts = $MIDO_ZOOKEEPER_HOSTS
root_key = $MIDO_ZOOKEEPER_ROOT_KEY
EOF


mn-conf set -t default <<EOF
zookeeper.zookeeper_hosts="$MIDO_ZOOKEEPER_HOSTS"
agent.midolman.bgp_keepalive=1s
agent.midolman.bgp_holdtime=3s
agent.midolman.bgp_connect_retry=1s
agent.midolman.lock_memory=false
agent.midolman.simulation_threads=2
agent.loggers.root=DEBUG
agent.haproxy_health_monitor.namespace_cleanup=true
agent.haproxy_health_monitor.health_monitor_enable=true
agent.haproxy_health_monitor.haproxy_file_loc=/etc/midolman/l4lb/
EOF

echo "Starting agent!"
exec /sbin/init

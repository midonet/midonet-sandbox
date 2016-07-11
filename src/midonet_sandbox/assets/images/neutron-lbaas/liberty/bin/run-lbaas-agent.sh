#!/bin/bash -x
echo 'Waiting for midonet_host_id file to appear...'
while [ ! -f /etc/sandbox/midonet_host_id.properties ] ; do
    sleep 1
done
cp /etc/sandbox/midonet_host_id.properties /etc/midonet_host_id.properties

neutron-lbaas-agent --debug --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/services/loadbalancer/haproxy/lbaas_agent.ini

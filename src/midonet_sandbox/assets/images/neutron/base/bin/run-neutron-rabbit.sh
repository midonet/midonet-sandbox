#!/bin/bash -x

# Replace the fake rpc for the rabbit one.
sed -i "s/rpc_backend.*/rpc_backend = rabbit\nrabbit_host = 172.17.0.1\nrabbit_user = guest\nrabbit_password = guest/g" /etc/neutron/plugins/midonet/midonet.ini

# Configure the HA proxy service provider
sed -i -e "\$a[service_providers]" /etc/neutron/plugins/midonet/midonet.ini
sed -i -e "\$aservice_provider = LOADBALANCER:Haproxy:neutron_lbaas.services.loadbalancer.drivers.haproxy.plugin_driver.HaproxyOnHostPluginDriver:default" /etc/neutron/plugins/midonet/midonet.ini

mkdir -p /var/lib/mysql

# keep mariadb in-memory for performance unless is set to false
if [ "${MARIADB_IN_MEM}" != "false" ]; then
    mount -t tmpfs -o size=1024m tmpfs /var/lib/mysql
    tar -C / -zxf /mariadb-data.tgz
fi

exec /sbin/init

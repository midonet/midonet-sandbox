#!/bin/bash -x

mkdir -p /var/lib/mysql

# keep mariadb in-memory for performance unless is set to false
if [ "${MARIADB_IN_MEM}" != "false" ]; then
    mount -t tmpfs -o size=1024m tmpfs /var/lib/mysql
    tar -C / -zxf /mariadb-data.tgz
fi

cd /var/lib/neutron
/bin/mkdir -p /var/lock/neutron /var/log/neutron /var/lib/neutron
/etc/init.d/neutron-server systemd-start


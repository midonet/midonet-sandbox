#!/bin/bash -x

mkdir -p /var/lib/mysql

# keep mariadb in-memory for performance unless is set to false
if [ "${MARIADB_IN_MEM}" != "false" ]; then
    mount -t tmpfs -o size=1024m tmpfs /var/lib/mysql
    tar -C / -zxf /mariadb-data.tgz
fi

exec /sbin/init

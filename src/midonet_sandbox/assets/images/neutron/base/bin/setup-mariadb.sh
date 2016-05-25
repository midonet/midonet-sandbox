#!/usr/bin/env bash

/usr/bin/mysqld_safe &
mysqladmin -w120 --connect-timeout 1 -h localhost -uroot -proot -f drop neutron
mysqladmin -w120 --connect-timeout 1 -h localhost -uroot -proot -f create neutron
neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/midonet/midonet.ini upgrade head
midonet-db-manage --config-file /etc/neutron/plugins/midonet/midonet.ini upgrade head
mysqladmin -uroot -proot -h localhost shutdown
wait

tar zcf /mariadb-data.tgz /var/lib/mysql

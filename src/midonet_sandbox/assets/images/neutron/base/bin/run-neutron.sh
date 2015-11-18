#!/bin/bash -x

# Prepare neutron database before starting
mysqladmin -w120 --connect-timeout 1 -h mariadb -uroot -proot -f drop neutron
mysqladmin -w120 --connect-timeout 1 -h mariadb -uroot -proot -f create neutron

neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/midonet/midonet.ini upgrade head
midonet-db-manage --config-file /etc/neutron/plugins/midonet/midonet.ini upgrade head

exec /sbin/init

#!/usr/bin/env bash

set -ex

/usr/bin/mysqld_safe &
mysqladmin -w120 --connect-timeout 1 -h localhost -uroot -proot -f drop neutron || true
mysqladmin -w120 --connect-timeout 1 -h localhost -uroot -proot -f create neutron
mysql -u root -proot -e "GRANT ALL PRIVILEGES ON *.* TO root@localhost IDENTIFIED BY 'root'"
neutron-db-manage --config-file /etc/neutron/neutron.conf \
                  --config-file /etc/neutron/plugins/midonet/midonet.ini upgrade head
neutron-db-manage --config-file /etc/neutron/neutron.conf \
                  --config-file /etc/neutron/plugins/midonet/midonet.ini \
                  --subproject networking-midonet upgrade head

mysqladmin -uroot -proot -h localhost shutdown
wait

tar zcf /mariadb-data.tgz /var/lib/mysql

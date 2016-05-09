#!/bin/bash -x

export SERVICE_USER=admin
export SERVICE_TENANT_NAME=admin
export SERVICE_PASSWORD=admin
export IDENTITY_URL=http://keystone:35357/v2.0/
export OS_URL=http://neutron:9696/
export K8S_API=http://172.17.0.1:8080
export PS1="\u@\h \W(keystone_admin)\$ "

# Raven stops if any problem occurs login into the keystone
# Since we have to wait until the provisioning script has run,
# we have to set this sleep
sleep 60

raven > /var/log/raven/raven.log

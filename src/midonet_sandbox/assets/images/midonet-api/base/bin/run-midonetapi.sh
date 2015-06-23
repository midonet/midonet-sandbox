#!/bin/bash

# Update ZK hosts in case they were linked to this container
if [[ `env | grep _PORT_2181_TCP_ADDR` ]]; then
    ZK_HOSTS="$(env | grep _PORT_2181_TCP_ADDR | sed -e 's/.*_PORT_2181_TCP_ADDR=//g' -e 's/^.*/&:2181/g')"
    ZK_HOSTS="$(echo $ZK_HOSTS | sed 's/ /,/g')"
fi

IP=${LISTEN_ADDRESS:-`hostname --ip-address`}

if [ -z "$ZK_HOSTS" ]; then
    echo "No Zookeeper hosts specified neither by ENV VAR nor by linked containers"
    exit 1
fi

# Edit web.xml

MIDONET_API_CFG=/usr/share/midonet-api/WEB-INF/web.xml


sudo sed -i -e "/<param-name>rest_api-base_uri<\/param-name>/{n;s%.*%    <param-value>http://"$IP":8080/midonet-api</param-value>%g}" $MIDONET_API_CFG
sudo sed -i -e "/<param-name>zookeeper-zookeeper_hosts<\/param-name>/{n;n;s%.*%    <param-value>"$ZK_HOSTS"</param-value>%g}" $MIDONET_API_CFG
sudo sed -i -e "s/org.midonet.api.auth.keystone.v2_0.KeystoneService/org.midonet.cluster.auth.MockAuthService/g" $MIDONET_API_CFG

# Edit JAVA_OPTS
CATALINA_SH=/usr/share/tomcat7/bin/catalina.sh
sudo sed -i -e "/#JAVA_OPTS/{n;s%.*%JAVA_OPTS='$JAVA_OPTS -Djava.security.egd=file:/dev/./urandom'%g}" $CATALINA_SH

# Run tomcat
exec /usr/lib/jvm/default-java/bin/java -Djava.util.logging.config.file=/var/lib/tomcat7/conf/logging.properties -Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager -Djava.security.egd=file:/dev/./urandom -Djava.endorsed.dirs=/usr/share/tomcat7/endorsed -classpath /usr/share/tomcat7/bin/bootstrap.jar:/usr/share/tomcat7/bin/tomcat-juli.jar -Dcatalina.base=/var/lib/tomcat7 -Dcatalina.home=/usr/share/tomcat7 -Djava.io.tmpdir=/tmp/tomcat7-tomcat7-tmp org.apache.catalina.startup.Bootstrap start

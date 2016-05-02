FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

COPY bin/run-raven.sh /run-raven.sh

RUN apt-get -qy update && apt-get -qy install git python3-setuptools python3-pip
RUN git clone http://github.com/midonet/kuryr /opt/kuryr -b k8s
RUN cd /opt/kuryr && pip3 install -r requirements.txt
RUN sed -i s/logging.INFO/logging.DEBUG/ /opt/kuryr/kuryr/__init__.py
RUN cd /opt/kuryr && python3 setup.py install
RUN mkdir -p /var/log/raven

CMD ["/run-raven.sh"]

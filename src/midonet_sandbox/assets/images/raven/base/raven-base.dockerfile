FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

COPY bin/run-raven.sh /run-raven.sh

RUN apt-get -qy update && apt-get -qy install curl git python3 gcc python3-dev
RUN git clone http://github.com/midonet/kuryr /opt/kuryr -b k8s
RUN curl https://bootstrap.pypa.io/get-pip.py | python3 -
RUN sed -i s/logging.INFO/logging.DEBUG/ /opt/kuryr/kuryr/__init__.py
RUN cd /opt/kuryr && pip3 install .
RUN mkdir -p /var/log/raven

CMD ["/run-raven.sh"]

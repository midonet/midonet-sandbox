FROM sandbox/midolman:base
MAINTAINER MidoNet (http://midonet.org)
RUN apt-get remove -y midolman
RUN apt-get install -yf midolman

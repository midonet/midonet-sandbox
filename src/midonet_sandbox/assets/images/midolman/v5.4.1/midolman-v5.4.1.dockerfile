FROM sandbox/midolman:base
MAINTAINER MidoNet (http://midonet.org)

RUN git clone https://github.com/midonet/midonet.git /midonet_src
WORKDIR /midonet_src
RUN git checkout origin/stable/v5.4.1
RUN git checkout -b v5.4.1
RUN sudo apt-get install -y ruby-ronn
RUN apt-get install -y ruby-dev build-essential
RUN gem install --no-ri --no-rdoc fpm
RUN ./gradlew -x test debian
RUN sudo dpkg -i ./midolman/build/packages/midolman_*_all.deb

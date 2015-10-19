# Midonet Sandbox

## Getting started

Clone the git repository and install the package with:

    $ python setup.py install

You may want to use a virtual env for it:

    $ mkdir venv
    $ virtualenv venv/
    $ cd venv ; source bin/activate


Once you installed it, you can check the available flavours:

    $ sandbox-manage flavours-list
    [07-02 10:51:54] INFO - Cannot read ~/.midonet-sandboxrc
    [07-02 10:51:54] INFO - Using default settings
    +-----------------+
    | Flavours        |
    |-----------------|
    | master+kilo     |
    | master+liberty  |
    | 2015.03+kilo    |
    +-----------------+


You may want to check which components these flavours provide:

    $ sandbox-manage flavours-list --details
    [07-02 10:54:01] INFO - Cannot read ~/.midonet-sandboxrc
    [07-02 10:54:01] INFO - Using default settings
    +--------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
    | Flavour      | Components                                                                                                                                      |
    |--------------+-------------------------------------------------------------------------------------------------------------------------------------------------|
    | master+kilo  | 1x sandbox/keystone:kilo, 2x sandbox/cassandra:master, 1x sandbox/midolman:master, 1x sandbox/midonet-api:master, 3x sandbox/zookeeper:master   |
    | 2015.03+kilo | 2x sandbox/cassandra:master, 1x sandbox/midolman:2015.03, 1x sandbox/keystone:kilo, 1x sandbox/midonet-api:2015.03, 3x sandbox/zookeeper:master |
    +--------------+-------------------------------------------------------------------------------------------------------------------------------------------------+

You can check if the required images are available in your docker installation:

    $ sandbox-manage images-list
    [07-02 10:58:04] INFO - Cannot read ~/.midonet-sandboxrc
    [07-02 10:58:04] INFO - Using default settings
    [07-02 10:58:06] ERROR - A <class 'requests.exceptions.ConnectionError'> occured: ('Connection aborted.', error(2, 'No such file or directory'))

As default, the sandbox will try to connect to a local Docker daemon via the unix socket.
In this case Docker was running in a VM, so let's specify this in the config file:

    $ cat config.cfg
    [sandbox]
    docker_socket = tcp://192.168.33.10:4243

     sandbox-manage -c config.cfg images-list
    [07-02 11:03:11] INFO - Loading configuration file: config.cfg
    [07-02 11:03:11] INFO - No images found


Ok, so let's build the required images for the flavour:

    $ sandbox-manage -c config.cfg build-all master+kilo
    [07-02 11:04:28] INFO - Loading configuration file: config.cfg
    [07-02 11:04:28] INFO - Building the following components: cassandra:master, midolman:master, midonet-api:master, zookeeper:master
    [07-02 11:04:28] INFO - Build started for cassandra:master, publish is False
    [07-02 11:04:28] INFO - Base image cassandra:base not found, skipping
    [07-02 11:04:28] INFO - Now building sandbox/cassandra:master
    Step 0 : FROM ubuntu:14.04
    [... cut ...]

If you modify some of the images (dockerfiles or associated files), be sure to do `python setup.py install`, then you can build them independently. :

    $ python setup.py install
    $ sandbox-manager -c config.cfg build midonet:master
    [07-10 16:18:16] INFO - Loading configuration file: config.cfg
    [07-10 16:18:16] INFO - Build started for midolman:master, publish is False
    [07-10 16:18:16] INFO - Now building sandbox/midolman:base
    Step 0 : FROM ubuntu-upstart:14.04
    [... cut ...]


**NOTE: If creating the images is very slow, try setting the nofile limit to 1024 in /etc/init/docker.conf and restart docker ([bug report](https://bugs.launchpad.net/ubuntu/+source/apt/+bug/1332440)).**

Now all the required images are available:

    $ sandbox-manage -c config.cfg images-list
    [07-02 11:10:56] INFO - Loading configuration file: config.cfg
    +----------------------------+---------------+
    | Image                      | Created       |
    |----------------------------+---------------|
    | sandbox/zookeeper:master   | a minute ago  |
    | sandbox/midonet-api:master | 2 minutes ago |
    | sandbox/midonet-api:base   | 4 minutes ago |
    | sandbox/midolman:master    | 4 minutes ago |
    | sandbox/midolman:base      | 7 minutes ago |
    | sandbox/cassandra:master   | 7 minutes ago |
    +----------------------------+---------------+


and we can start a sandbox based on this flavour, let's call it staging.

**NOTE: Before running the midolman component make sure the openvswitch module has been loaded on the host**

    (where the docker daemon runs)
    $ sudo modprobe openvswitch

---

    $ sandbox-manage -c config.cfg run master+kilo --name staging
    [07-02 11:20:36] INFO - Loading configuration file: config.cfg
    [07-02 11:20:36] INFO - Spawning master+kilo sandbox
    Creating mnsandboxstaging_cassandra1_1...
    Creating mnsandboxstaging_cassandra2_1...
    Creating mnsandboxstaging_zookeeper1_1...
    Creating mnsandboxstaging_zookeeper2_1...
    Creating mnsandboxstaging_zookeeper3_1...
    Creating mnsandboxstaging_api_1...
    Creating mnsandboxstaging_midolman_1...
    +-----------+-------------------------------+----------------------------+----------------------------------------------+-------------+
    | Sandbox   | Name                          | Image                      | Ports                                        | Ip          |
    |-----------+-------------------------------+----------------------------+----------------------------------------------+-------------|
    | staging   | mnsandboxstaging_midolman_1   | sandbox/midolman:master    | tcp/22                                       | 172.17.0.28 |
    | staging   | mnsandboxstaging_api_1        | sandbox/midonet-api:master | tcp/22,tcp/8080                              | 172.17.0.27 |
    | staging   | mnsandboxstaging_zookeeper3_1 | sandbox/zookeeper:master   | tcp/2181,tcp/2888,tcp/3888                   | 172.17.0.26 |
    | staging   | mnsandboxstaging_zookeeper2_1 | sandbox/zookeeper:master   | tcp/2181,tcp/2888,tcp/3888                   | 172.17.0.25 |
    | staging   | mnsandboxstaging_zookeeper1_1 | sandbox/zookeeper:master   | tcp/2181,tcp/2888,tcp/3888                   | 172.17.0.24 |
    | staging   | mnsandboxstaging_cassandra2_1 | sandbox/cassandra:master   | tcp/7000,tcp/7001,tcp/7199,tcp/9042,tcp/9160 | 172.17.0.23 |
    | staging   | mnsandboxstaging_cassandra1_1 | sandbox/cassandra:master   | tcp/7000,tcp/7001,tcp/7199,tcp/9042,tcp/9160 | 172.17.0.22 |
    +-----------+-------------------------------+----------------------------+----------------------------------------------+-------------+

To stop the sandbox:

    $ sandbox-manage -c config.cfg stop staging      # or stop-all to stop all the running sandbox
    [07-02 11:23:19] INFO - Loading configuration file: config.cfg
    [07-02 11:23:19] INFO - Sandbox staging - Stopping container api_1
    [07-02 11:23:20] INFO - Sandbox staging - Stopping container zookeeper3_1
    [07-02 11:23:30] INFO - Sandbox staging - Stopping container zookeeper2_1
    [07-02 11:23:40] INFO - Sandbox staging - Stopping container zookeeper1_1
    [07-02 11:23:50] INFO - Sandbox staging - Stopping container cassandra2_1
    [07-02 11:23:52] INFO - Sandbox staging - Stopping container cassandra1_1

The `stop` command will try to gracefully stop the container. However, this might be a slow operation as the host waits for the container command to return. In a development session, you might not care about the state of the container after stopping it so you have the option to just kill it without waiting for the container to return.

    $ sandbox-manage -c config.cfg kill staging     # or kill-all to kill all the running sandbox

### Provide your own flavour

To provide your own flavour, just create a folder, place your flavour yml file in it (you may want to copy and modifify a base one
you find [Here](https://github.com/midokura/midonet-sandbox/tree/master/src/midonet_sandbox/assets/composer/flavours), and specify it in
the configuration file:


    $ ls /workplace/midonet-sandbox/venv/extra
    zk-only.yml

    $ cat config.cfg
    [sandbox]
    extra_flavours=/workplace/midonet-sandbox/venv/extra
    docker_socket = tcp://192.168.33.10:4243

    $ sandbox-manage -c config.cfg flavours-list --details
    [07-02 11:41:30] INFO - Loading configuration file: config.cfg
    +--------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
    | Flavour      | Components                                                                                                                                      |
    |--------------+-------------------------------------------------------------------------------------------------------------------------------------------------|
    | zk-only      | 3x sandbox/zookeeper:master                                                                                                                     |
    | master+kilo  | 1x sandbox/keystone:kilo, 2x sandbox/cassandra:master, 1x sandbox/midolman:master, 1x sandbox/midonet-api:master, 3x sandbox/zookeeper:master   |
    | 2015.03+kilo | 2x sandbox/cassandra:master, 1x sandbox/midolman:2015.03, 1x sandbox/keystone:kilo, 1x sandbox/midonet-api:2015.03, 3x sandbox/zookeeper:master |
    +--------------+-------------------------------------------------------------------------------------------------------------------------------------------------+

The flavour file will inherit and reuse base components. You refer to base yml files using the $BASE variable:

    $  cat /workplace/midonet-sandbox/venv/extra/zk-only.yml
    zookeeper1:
      extends:
        file: $BASE/zookeeper.yml
        service: zookeeper
      image: sandbox/zookeeper:master
      volumes:
      - /zoo/conf/
      environment:
      - ZOO_ID=1
      ports:
      - 9000:2181

    [ .. cut ...]

### Provide your own component
Same way, you can provide your own components creating a components directory and passing it in the configuration file
using the *extra_components* parameter.

The component directory must follow a structure like ($component/$version/$(component-version).dockerfile).
For example, if want to provide your zookeeper component tagging it as master, the associated components directory
will be something like:

    extra-components
    └── myzookeeper
        └── master
            ├── bin
            │       └── run-zookeeper.sh
            └── myzookeeper-master.dockerfile


This specify the myzookeeper:master component (docker image) that you can use in your flavours.

The configuration file will look similar to:

    $ cat config.cfg
    [sandbox]
    extra_flavours=/workplace/midonet-sandbox/venv/extra
    extra_components=/workplace/midonet-sandbox/venv/extra-components
    docker_socket = tcp://192.168.33.10:4243


### Provide an override

An override is a directory that contains a directory for each component to override (the name must match the 'service' parameter defined
in the flavour yml file)

    $ tree /workplace/midonet-sandbox/venv/myoverride
    /workplace/midonet-sandbox/venv/myoverride
    ├── midolman
    │   ├── midolman-master.deb
    │   └── override.sh
    └── zookeeper
        └── override.sh


Each component folder contains the *override.sh* script and may contain files.

When an override is applied to a sandbox each container mounts the specific override folder in the */override* path
and change its **CMD to /override/override.sh**.

Typical uses of an override is to pass a new debian package and install it, or change a configuration file before starting the service:

    $ cat /workplace/midonet-sandbox/venv/myoverride/midolman/override.sh
    #!/bin/sh
    dpkg -i /override/midolman-master.deb
    exec ./run-midolman.sh

**NOTE: if you call another script within your override to start an upstart service (e.g. run-midolman.sh calls /sbin/init to spawn any upstart service), do it through the *exec* command (not a regular invocation).**


To apply an override to a sandbox you can use the --override parameter:

    $ sandbox-manage -c config.cfg run master+kilo --name staging --override /workplace/midonet-sandbox/venv/myoverride
    [07-02 11:52:59] INFO - Loading configuration file: config.cfg
    [07-02 11:52:59] INFO - Spawning master+kilo sandbox with override /workplace/midonet-sandbox/venv/myoverride
    Recreating mnsandboxstaging_cassandra1_1...
    Recreating mnsandboxstaging_cassandra2_1...
    [ ... cut ... ]


### Provide a provisioning script
You may want to configure a virtual topology once the sandbox is up&running.
An handy way to achieve this would be passing a provisioning script at the command line.
This script will be run just after all the containers are up and will take care of inizializing the virtual topology.
A command line will simply looks similar to:

    $ sandbox-manage -c config.cfg run master+kilo --name staging --provision venv/myoverride/provision.sh


Eg: The following provisioning script will create a tunnel zone and register two hosts to it:

    #!/bin/sh
    set -uxe

    # Wait that all services are up&running
    sleep 30

    CLI_HOST="$(docker ps | grep midonet-api | awk '{print $1}')"
    CLI_COMMAND="docker exec $CLI_HOST midonet-cli -A -e"

    HOST0_ID=$($CLI_COMMAND host list | head -n 1 | awk '{print $2}')
    HOST1_ID=$($CLI_COMMAND host list | tail -n 1 | awk '{print $2}')
    HOST0_NAME=$($CLI_COMMAND host $HOST0_ID show name)
    HOST1_NAME=$($CLI_COMMAND host $HOST1_ID show name)

    MIDOLMAN1_IP="$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' $HOST0_NAME)"
    MIDOLMAN2_IP="$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' $HOST1_NAME)"

    # Create the tunnelzone and add midolman
    $CLI_COMMAND tunnel-zone create name default type vxlan

    TZONEID=$($CLI_COMMAND tunnel-zone list | awk '{print $2}')

    $CLI_COMMAND tunnel-zone $TZONEID add member host $HOST0_ID address $MIDOLMAN1_IP
    $CLI_COMMAND tunnel-zone $TZONEID add member host $HOST1_ID address $MIDOLMAN2_IP

### Pushing and pulling from an external registry

By default, sandbox-manage pulls and pushes to the default registry in docker `index.docker.io`. If you need to interact with a different docker registry, a couple of config parameters should be added to the `sandbox.conf` file. 
An example of how the configuration file looks like in that case is displayed below.

    $ cat sandbox.conf
    [sandbox]
    extra_flavours=sandbox/flavors
    extra_components=sandbox/components
    docker_registry=your.own.artifactory.company.com
    docker_insecure_registry=True

    

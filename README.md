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
    +--------------+
    | Flavours     |
    |--------------|
    | master+juno  |
    | 2015.03+juno |
    +--------------+

   
You may want to check which components these flavours provide:

    $ sandbox-manage flavours-list --details                                                                    
    [07-02 10:54:01] INFO - Cannot read ~/.midonet-sandboxrc
    [07-02 10:54:01] INFO - Using default settings
    +--------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
    | Flavour      | Components                                                                                                                                      |
    |--------------+-------------------------------------------------------------------------------------------------------------------------------------------------|
    | master+juno  | 1x sandbox/keystone:kilo, 2x sandbox/cassandra:master, 1x sandbox/midolman:master, 1x sandbox/midonet-api:master, 3x sandbox/zookeeper:master   |
    | 2015.03+juno | 2x sandbox/cassandra:master, 1x sandbox/midolman:2015.03, 1x sandbox/keystone:kilo, 1x sandbox/midonet-api:2015.03, 3x sandbox/zookeeper:master |
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
 
    $ sandbox-manage -c config.cfg build-all master+juno                                                         
    [07-02 11:04:28] INFO - Loading configuration file: config.cfg
    [07-02 11:04:28] INFO - Building the following components: cassandra:master, midolman:master, midonet-api:master, zookeeper:master
    [07-02 11:04:28] INFO - Build started for cassandra:master, publish is False
    [07-02 11:04:28] INFO - Base image cassandra:base not found, skipping
    [07-02 11:04:28] INFO - Now building sandbox/cassandra:master
    Step 0 : FROM ubuntu:14.04
    [... cut ...]
    
If you modify some of the images (dockerfiles or associated files), you can build them independently:

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

    $ sandbox-manage -c config.cfg run master+juno --name staging                                                
    [07-02 11:20:36] INFO - Loading configuration file: config.cfg
    [07-02 11:20:36] INFO - Spawning master+juno sandbox
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
    | master+juno  | 1x sandbox/keystone:kilo, 2x sandbox/cassandra:master, 1x sandbox/midolman:master, 1x sandbox/midonet-api:master, 3x sandbox/zookeeper:master   |
    | 2015.03+juno | 2x sandbox/cassandra:master, 1x sandbox/midolman:2015.03, 1x sandbox/keystone:kilo, 1x sandbox/midonet-api:2015.03, 3x sandbox/zookeeper:master |
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
    /run-midolman.sh


To apply an override to a sandbox you can use the --override parameter:

    $ sandbox-manage -c config.cfg run master+juno --name staging --override /workplace/midonet-sandbox/venv/myoverride 
    [07-02 11:52:59] INFO - Loading configuration file: config.cfg
    [07-02 11:52:59] INFO - Spawning master+juno sandbox with override /workplace/midonet-sandbox/venv/myoverride
    Recreating mnsandboxstaging_cassandra1_1...
    Recreating mnsandboxstaging_cassandra2_1...
    [ ... cut ... ]

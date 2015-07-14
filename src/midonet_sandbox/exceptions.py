# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

class Sandbox(Exception):
    pass


class ImageNotFound(Sandbox):
    pass


class FlavourNotFound(Sandbox):
    pass


class ContainerNotFound(Sandbox):
    pass

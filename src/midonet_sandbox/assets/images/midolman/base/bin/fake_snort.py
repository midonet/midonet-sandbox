#!/usr/bin/env python
#
# Copyright 2015 Midokura SARL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from setproctitle import setproctitle
import pcap
import binascii
import argparse

parser = argparse.ArgumentParser(
    description='A fake snort to mirror some packets, block others.')
parser.add_argument('--interface', dest='iface',
                    metavar='DEV', type=str, nargs=1,
                    required=True,
                    help='Interface to listen on')
parser.add_argument('--block-pattern', dest='pattern',
                    metavar='PATTERN', type=str, nargs=1,
                    required=True,
                    help='Pattern to block in packets')
parser.add_argument('--debug', dest='debug',
                    action='store_const',
                    const=True, default=False,
                    help='Enabled debug output')

args = parser.parse_args()

interface = args.iface[0]
pattern = args.pattern[0]

setproctitle('fake_snort_' + interface)

# have to use pcap rather than raw socket, because kernel
# strips vlan info from raw socket packets
capture = pcap.pcap(interface)
for c in capture:
    if c is None:
        continue
    (ts, pckt) = c
    hexed = binascii.hexlify(pckt)
    if args.debug:
        print "Received: %s" % hexed
    if not pattern in hexed:
        capture.sendpacket(str(pckt))
    else:
        print "Blocked packet"

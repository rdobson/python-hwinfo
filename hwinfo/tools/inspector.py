#!/usr/bin/env python

from argparse import ArgumentParser
import paramiko

from hwinfo.pci import PCIDevice
from hwinfo.pci.lspci import *

def remote_command(host, username, password, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password, timeout=10)
    cmdstr = ' '.join(cmd)
    print "Executing '%s' on host '%s'" % (cmdstr, host)
    _, stdout, stderr = client.exec_command(cmdstr)
    output = stdout.readlines()
    error = stderr.readlines()
    if error:
        print "stderr: %s" % error
    client.close()
    return ''.join(output)

def local_command(cmd):
    return cmd

class Host(object):

    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def exec_command(self, cmd):
        assert not self.host
        return local_command(cmd)

    def get_pci_devices(self):
        data = self.exec_command(['lspci', '-nnmm'])
        parser = LspciNNMMParser(data)
        devices = parser.parse_items()
        return [PCIDevice(device) for device in devices]

class RemoteHost(Host):

    def exec_command(self, cmd):
        return remote_command(self.host, self.username, self.password, cmd)


def main():
    """Entry Point"""

    parser = ArgumentParser(prog="hwinfo")
    parser.add_argument("cmd")
    parser.add_argument("host")
    parser.add_argument("username")
    parser.add_argument("password")

    args = parser.parse_args()

    host = RemoteHost(args.host, args.username, args.password)

    if args.cmd == 'list':
        devices = host.get_pci_devices()
        for device in devices:
            print device.get_info()



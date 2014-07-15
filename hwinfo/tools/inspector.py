#!/usr/bin/env python

from argparse import ArgumentParser
from prettytable import PrettyTable
import paramiko
import subprocess

from hwinfo.pci import PCIDevice
from hwinfo.pci.lspci import *

from hwinfo.host import dmidecode

def remote_command(host, username, password, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password, timeout=10)
    cmdstr = ' '.join(cmd)
    #print "Executing '%s' on host '%s'" % (cmdstr, host)
    _, stdout, stderr = client.exec_command(cmdstr)
    output = stdout.readlines()
    error = stderr.readlines()
    if error:
        raise Exception("stderr: %s" % error)
    client.close()
    return ''.join(output)

def local_command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        return str(stdout).strip()
    else:
        print "RC: %s" % process.returncode
        print stdout
        raise Exception("stderr: %s" % str(stderr))

class Host(object):

    def __init__(self, host='localhost', username=None, password=None):
        self.host = host
        self.username = username
        self.password = password

    def exec_command(self, cmd):
        if self.host == 'localhost':
            return local_command(cmd)
        else:
            return remote_command(self.host, self.username, self.password, cmd)

    def get_pci_devices(self):
        data = self.exec_command(['lspci', '-nnmm'])
        parser = LspciNNMMParser(data)
        devices = parser.parse_items()
        return [PCIDevice(device) for device in devices]

    def get_info(self):
        data = self.exec_command(['dmidecode'])
        parser = dmidecode.DmidecodeParser(data)
        print "test : '%s'" % parser
        rec = parser.parse()
        return rec

def pci_filter(devices, types):
    res = []
    for device in devices:
        for t in types:
            if device.get_pci_class().startswith(t):
                res.append(device)
                break
    return res

def pci_filter_for_nics(devices):
    nic_types = ['02']
    return pci_filter(devices, nic_types)

def pci_filter_for_storage(devices):
    storage_types = ['00', '01']
    return pci_filter(devices, storage_types)

def pci_filter_for_gpu(devices):
    gpu_types = ['03']
    return pci_filter(devices, gpu_types)

def rec_to_table(rec):
    table = PrettyTable(["Key", "Value"])
    table.align['Key'] = 'l'
    table.align['Value'] = 'l'
    for k, v in rec.iteritems():
        table.add_row([k, v])
    return table

def tabulate_pci_recs(recs):
    header = [
        'vendor_name',
        'vendor_id',
        'device_name',
        'device_id',
        'subvendor_name',
        'subvendor_id',
        'subdevice_name',
        'subdevice_id',
    ]
    table = PrettyTable(header)
    for rec in recs:
        vls = [rec[k] for k in header]
        table.add_row(vls)
    return table

def main():
    """Entry Point"""

    parser = ArgumentParser(prog="hwinfo")

    filter_choices = ['bios', 'nic', 'storage', 'gpu']
    parser.add_argument("-f", "--filter", choices=filter_choices)
    parser.add_argument("-m", "--machine", default='localhost')
    parser.add_argument("-u", "--username")
    parser.add_argument("-p", "--password")

    args = parser.parse_args()

    host = Host(args.machine, args.username, args.password)

    options = []

    if args.filter:
        filter_args = args.filter.split(',')
        for arg in filter_args:
            options.append(arg.strip())
    else:
        options = filter_choices

    if 'bios' in options:
        print "Bios Info:"
        print ""
        print rec_to_table(host.get_info())
        print ""

    if 'nic' in options:
        devices = pci_filter_for_nics(host.get_pci_devices())
        print "Ethernet Controller Info:"
        print ""
        print tabulate_pci_recs([dev.get_rec() for dev in devices])
        print ""

    if 'storage' in options:
        devices = pci_filter_for_storage(host.get_pci_devices())
        print "Storage Controller Info:"
        print ""
        print tabulate_pci_recs([dev.get_rec() for dev in devices])
        print ""

    if 'gpu' in options:
        devices = pci_filter_for_gpu(host.get_pci_devices())
        if devices:
            print "GPU Info:"
            print ""
            print tabulate_pci_recs([dev.get_rec() for dev in devices])
            print ""

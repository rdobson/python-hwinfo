#!/usr/bin/env python

from argparse import ArgumentParser
from prettytable import PrettyTable
import paramiko
import subprocess
import os

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

    def get_lspci_data(self):
        return self.exec_command(['lspci', '-nnmm'])

    def get_dmidecode_data(self):
        return self.exec_command(['dmidecode'])

    def get_pci_devices(self):
        data = self.get_lspci_data()
        parser = LspciNNMMParser(data)
        devices = parser.parse_items()
        return [PCIDevice(device) for device in devices]

    def get_info(self):
        data = self.get_dmidecode_data()
        parser = dmidecode.DmidecodeParser(data)
        rec = parser.parse()
        return rec

def search_for_file(dirname, filename):
    for root, _, files in os.walk(dirname):
        if filename in files:
            return os.path.join(root, filename)
    raise Exception("Could not find '%s' in directory '%s'" % (filename, dirname))

def read_from_file(filename):
    fh = open(filename, 'r')
    data = fh.read()
    fh.close()
    return data

class HostFromLogs(Host):

    def __init__(self, dirname):
        self.dirname = dirname

    def _load_from_file(self, filename):
        filename = search_for_file(self.dirname, filename)
        return read_from_file(filename)

    def get_lspci_data(self):
        return self._load_from_file('lspci-nnm.out')

    def get_dmidecode_data(self):
        return self._load_from_file('dmidecode.out')

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
    parser.add_argument("-f", "--filter", choices=filter_choices, help="Query a specific class.")
    parser.add_argument("-m", "--machine", default='localhost', help="Remote host address.")
    parser.add_argument("-u", "--username", help="Username for remote host.")
    parser.add_argument("-p", "--password", help="Password for remote host.")
    parser.add_argument("-l", "--logs", help="Path to the directory with the logfiles.")

    args = parser.parse_args()

    if args.logs:
        host = HostFromLogs(args.logs)
    else:
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

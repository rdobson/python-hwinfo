#!/usr/bin/env python

from argparse import ArgumentParser
from prettytable import PrettyTable
import paramiko
import subprocess
import os
import sys

from hwinfo.pci import PCIDevice
from hwinfo.pci.lspci import *

from hwinfo.host import dmidecode
from hwinfo.host import cpuinfo

def get_ssh_client(host, username, password, timeout=10):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password, timeout=timeout)
    return client

def remote_command(client, cmd):
    cmdstr = ' '.join(cmd)
    #print "Executing '%s' on host '%s'" % (cmdstr, host)
    _, stdout, stderr = client.exec_command(cmdstr)
    output = stdout.readlines()
    error = stderr.readlines()
    if error:
        raise Exception("stderr: %s" % error)
    return ''.join(output)

def local_command(cmd):
    cmdstr = ' '.join(cmd)
    process = subprocess.Popen(cmdstr, stdout=subprocess.PIPE, shell=True)
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
        self.client = None
        if self.is_remote():
            self.client = get_ssh_client(self.host, self.username, self.password)

    def __del__(self):
        if self.client:
            self.client.close()

    def is_remote(self):
        return self.host != 'localhost'

    def exec_command(self, cmd):
        if self.is_remote():
            return remote_command(self.client, cmd)
        else:
            return local_command(cmd)

    def get_lspci_data(self):
        return self.exec_command(['lspci', '-nnmm'])

    def get_dmidecode_data(self):
        return self.exec_command(['dmidecode'])

    def get_cpuinfo_data(self):
        return self.exec_command(['cat /proc/cpuinfo'])

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

    def get_cpu_info(self):
        data = self.get_cpuinfo_data()
        parser = cpuinfo.CPUInfoParser(data)
        return parser.parse_items()

class FileNotFound(Exception):
    pass

def search_for_file(dirname, filename):
    for root, _, files in os.walk(dirname):
        if filename in files:
            return os.path.join(root, filename)
    raise FileNotFound("Could not find '%s' in directory '%s'" % (filename, dirname))

def read_from_file(filename):
    fh = open(filename, 'r')
    data = fh.read()
    fh.close()
    return data

def parse_data(parser, data):
    p = parser(data)
    return p.parse_items()

def combine_recs(rec_list, key):
    """Use a common key to combine a list of recs"""
    final_recs = {}
    for rec in rec_list:
        rec_key = rec[key]
        if rec_key in final_recs:
            for k, v in rec.iteritems():
                if k in final_recs[rec_key] and final_recs[rec_key][k] != v:
                    raise Exception("Mis-match for key '%s'" % k)
                final_recs[rec_key][k] = v
        else:
            final_recs[rec_key] = rec
    return final_recs.values()


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

    def get_cpuinfo_data(self):
        return self._load_from_file('cpuinfo')

    def get_pci_devices(self):
        try:
            devs = super(HostFromLogs, self).get_pci_devices()
            return devs
        except FileNotFound:
            # Fall back to looking for the file lspci-vv.out
            print "***lspci-nnm.out found. Falling back to looking for lspci-vv.out and lspci-n.out.***"
            lspci_vv_recs = parse_data(LspciVVParser, self._load_from_file('lspci-vv.out'))
            lspci_n_recs = parse_data(LspciNParser, self._load_from_file('lspci-n.out'))
            all_recs = lspci_vv_recs + lspci_n_recs
            recs = combine_recs(all_recs, 'pci_device_bus_id')
            return [PCIDevice(rec) for rec in recs]


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

def tabulate_recs(recs, header):
    table = PrettyTable(header)
    for rec in recs:
        vls = [rec[k] for k in header]
        table.add_row(vls)
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
    return tabulate_recs(recs, header)

def tabulate_cpu_recs(recs):
    header = [
        'processor',
        'vendor_id',
        'cpu_family',
        'model',
        'stepping',
        'model_name',
        'cpu_mhz',
    ]
    return tabulate_recs(recs, header)

def print_unit(title, content):
    print "%s" % title
    print ""
    print content
    print ""

def main():
    """Entry Point"""

    parser = ArgumentParser(prog="hwinfo")

    filter_choices = ['bios', 'nic', 'storage', 'gpu', 'cpu']
    parser.add_argument("-f", "--filter", choices=filter_choices, help="Query a specific class.")
    parser.add_argument("-m", "--machine", default='localhost', help="Remote host address.")
    parser.add_argument("-u", "--username", help="Username for remote host.")
    parser.add_argument("-p", "--password", help="Password for remote host.")
    parser.add_argument("-l", "--logs", help="Path to the directory with the logfiles.")

    args = parser.parse_args()

    if args.logs:
        host = HostFromLogs(args.logs)
    else:
        if args.machine and not args.username or not args.password:
            print "Error: you must specify a username and password to query a remote machine."
            sys.exit(1)

        host = Host(args.machine, args.username, args.password)

    options = []

    if args.filter:
        filter_args = args.filter.split(',')
        for arg in filter_args:
            options.append(arg.strip())
    else:
        options = filter_choices

    if 'bios' in options:
        print_unit("Bios Info:", rec_to_table(host.get_info()))

    if 'cpu' in options:
        print_unit("CPU Info:", tabulate_cpu_recs(host.get_cpu_info()))

    if 'nic' in options:
        devices = pci_filter_for_nics(host.get_pci_devices())
        print_unit("Ethernet Controller Info:", tabulate_pci_recs([dev.get_rec() for dev in devices]))

    if 'storage' in options:
        devices = pci_filter_for_storage(host.get_pci_devices())
        print_unit("Storage Controller Info:", tabulate_pci_recs([dev.get_rec() for dev in devices]))

    if 'gpu' in options:
        devices = pci_filter_for_gpu(host.get_pci_devices())
        if devices:
            print_unit("GPU Info:", tabulate_pci_recs([dev.get_rec() for dev in devices]))

#!/usr/bin/env python

from argparse import ArgumentParser
import paramiko
import subprocess
import os
import sys
import tarfile
import tempfile
import shutil
import json

from prettytable import PrettyTable

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

def find_in_tarball(tarball, filename):
    tar = tarfile.open(tarball)
    members = tar.getmembers()
    tar.close()
    matches = []
    for m in members:
        if m.name.endswith(filename) and "/crash/" not in m.name:
            matches.append(m.name)

    if len(matches) > 1:
        raise Exception("Error: more than one match for that filename")

    if not matches:
        raise FileNotFound("Cound not find %s in %s" % (filename, tarball))
    return matches.pop()

def read_files_from_tarball(tarball, files):
    tar = tarfile.open(tarball)
    tmpdir = tempfile.mkdtemp()


    file_data = {}
    for f in files:
        tar.extract(f, tmpdir)
        file_data[os.path.basename(f)] = read_from_file("%s/%s" % (tmpdir, f))

    tar.close()
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)
    return file_data

def read_from_tarball(tarball, filename):
    tar = tarfile.open(tarball)
    data = None
    tmpdir = tempfile.mkdtemp()

    tar.extract(filename, tmpdir)
    data = read_from_file("%s/%s" % (tmpdir, filename))

    tar.close()
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)

    return data

def parse_kvp_string(data):
    rec = {}
    lines = data.split('\n')
    for line in lines:
        if not line:
            continue
        k, v = line.split('=')
        rec[k] = v.strip("'")
    return rec

class Host(object):

    client = None

    def __init__(self, host='localhost', username=None, password=None):
        self.host = host
        self.username = username
        self.password = password
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

    def get_os_data(self):
        return self.exec_command(['cat', '/etc/xensource-inventory'])

    def get_os_info(self):
        rec = {}
        os_rec = parse_kvp_string(self.get_os_data())
        rec['os'] = os_rec['PRODUCT_BRAND']
        rec['version'] = os_rec['PRODUCT_VERSION']
        rec['build'] = os_rec['BUILD_NUMBER']
        return rec

    def get_pci_devices(self):
        data = self.get_lspci_data()
        parser = LspciNNMMParser(data)
        devices = parser.parse_items()
        return [PCIDevice(device) for device in devices]

    def get_info(self):
        data = self.get_dmidecode_data()
        parser = dmidecode.DmidecodeParser(data)
        rec = parser.parse()
        #Count sockets
        if 'socket_designation' in rec:
            rec['socket_count'] = len(rec['socket_designation'].split(','))

        try:
            os_rec = self.get_os_info()
            for k, v in os_rec.iteritems():
                rec[k] = v
        except Exception:
            #Ignore failures. Only supports XS right now.
            pass

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

    def get_os_data(self):
        return self._load_from_file('xensource-inventory')

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

class HostFromTarball(HostFromLogs):

    fdata = {}

    def __init__(self, filename, preload=True):
        self.tarloc = filename
        pre_load_files = [
            'lspci-nnm.out',
            'lspci-vv.out',
            'lspci-n.out',
            'dmidecode.out',
            'cpuinfo',
            'xensource-inventory'
        ]

        if preload:
            self._preload_files(pre_load_files)

    def _preload_files(self, filenames):
        paths = []
        for f in filenames:
            try:
                filepath = find_in_tarball(self.tarloc, f)
                paths.append(filepath)
            except FileNotFound:
                continue
        self.fdata = read_files_from_tarball(self.tarloc, paths)

    def _load_from_file(self, filename):
        """Find filename in tar, and load it"""
        if filename in self.fdata:
            return self.fdata[filename]
        else:
            filepath = find_in_tarball(self.tarloc, filename)
            return read_from_tarball(self.tarloc, filepath)

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
    storage_types = ['00', '01', '0c04', '0c06']
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
        'device_bus_id',
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

def create_unit(title, content):
    return "\n%s\n\n%s\n" % (str(title), str(content))

def validate_args(args):
    if args.machine != 'localhost':
        if not args.username or not args.password:
            print "Error: you must specify a username and password to query a remote machine."
            sys.exit(1)

def system_info(host, options):
    info = []

    if 'bios' in options:
        info.append(create_unit("Bios Info:", rec_to_table(host.get_info())))

    if 'cpu' in options:
        info.append(create_unit("CPU Info:", tabulate_cpu_recs(host.get_cpu_info())))

    if 'nic' in options:
        devices = pci_filter_for_nics(host.get_pci_devices())
        info.append(create_unit("Ethernet Controller Info:", tabulate_pci_recs([dev.get_rec() for dev in devices])))

    if 'storage' in options:
        devices = pci_filter_for_storage(host.get_pci_devices())
        info.append(create_unit("Storage Controller Info:", tabulate_pci_recs([dev.get_rec() for dev in devices])))

    if 'gpu' in options:
        devices = pci_filter_for_gpu(host.get_pci_devices())
        if devices:
            info.append(create_unit("GPU Info:", tabulate_pci_recs([dev.get_rec() for dev in devices])))

    return "".join(info).strip()

def export_system_info(host, options):
    rec = {}

    if 'bios' in options:
        rec["bios"] = host.get_info()

    if 'cpu' in options:
        rec["cpu"] = host.get_cpu_info()

    if 'nic' in options:
        devices = pci_filter_for_nics(host.get_pci_devices())
        rec["nics"] = [dev.get_rec() for dev in devices]

    if 'storage' in options:
        devices = pci_filter_for_storage(host.get_pci_devices())
        rec["storage_controllers"] = [dev.get_rec() for dev in devices]

    if 'gpu' in options:
        devices = pci_filter_for_gpu(host.get_pci_devices())
        rec["gpus"] = [dev.get_rec() for dev in devices]

    return json.dumps(rec, indent=4, separators=(',', ': '))

def main():
    """Entry Point"""

    parser = ArgumentParser(prog="hwinfo")

    filter_choices = ['bios', 'nic', 'storage', 'gpu', 'cpu']
    parser.add_argument("-f", "--filter", choices=filter_choices, help="Query a specific class.")
    parser.add_argument("-m", "--machine", default='localhost', help="Remote host address.")
    parser.add_argument("-u", "--username", help="Username for remote host.")
    parser.add_argument("-p", "--password", help="Password for remote host.")
    parser.add_argument("-l", "--logs", help="Path to the directory with the logfiles.")
    parser.add_argument("-e", "--export", action="store_true", help="Export result in JSON format.")

    args = parser.parse_args()
    validate_args(args)

    if args.logs:
        if ".tar" in args.logs:
            host = HostFromTarball(args.logs)
        else:
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

    if args.export:
        print export_system_info(host, options)
    else:
        print system_info(host, options)

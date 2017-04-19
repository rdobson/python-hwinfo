[![Build Status](https://travis-ci.org/rdobson/python-hwinfo.svg?branch=master)](https://travis-ci.org/rdobson/python-hwinfo)
[![Coverage Status](https://coveralls.io/repos/rdobson/python-hwinfo/badge.png)](https://coveralls.io/r/rdobson/python-hwinfo)

python-hwinfo
======

This is a python library for inspecting hardware and devices by parsing 
the outputs of system utilities such as lspci and dmidecode.


Installation
------------
This package can be installed using pip either directly from this repository
or from the latest published version on PyPi:
    
    pip install python-hwinfo

Or,

    pip install git+https://github.com/rdobson/python-hwinfo.git


Library Usage
-----
The library consists of a number of command parsers, and a number of higher-level
objects. The parsers simply return a record, or a list of records associated with
a particular command output. The higher-level objects are populated with the records
obtained from a command output and include additional logic.

For example, to parse a list of PCI devices:

    from hwinfo.pci import PCIDevice
    from hwinfo.pci.lspci import LspciNNMMParser
    from subprocess import check_output

    # Obtain the output of lspci -nnmm from somewhere
    lspci_output = check_output(["lspci", "-nnmm"])

    # Parse the output using the LspciNNMMParser object
    parser = LspciNNMMParser(lspci_output)
    device_recs = parser.parse_items()

    # Instantiate the records as PCI devices
    pci_devs = [PCIDevice(device_rec) for device_rec in device_recs]

    # Use the PCIDevice class to query info for subdevices
    for dev in pci_devs:
        if dev.is_subdevice():
            print dev.get_info()


CLI
---
Along with the classes for parsing/inspecting objects, the library also includes
a simple CLI tool which can be used for inspecting local, remote and captured hosts.

For inspecting the hardware present on a local machine, execute:

    $> hwinfo
    $>
    Bios Info:

    +----------------------+--------------------------------------+
    | Key                  | Value                                |
    +----------------------+--------------------------------------+
    | bios_vendor_name     | Dell Inc.                            |
    | system_product_name  | Precision T3610                      |
    | system_serial_number | 2Q2R212                              |
    | system_uuid          | 4C4C4544-0051-3210-8052-B2C04F323132 |
    | system_manufacturer  | Dell Inc.                            |
    | bios_release_date    | 02/28/2014                           |
    | bios_version         | A06                                  |
    +----------------------+--------------------------------------+

    CPU Info:

    +-----------+--------------+------------+-------+----------+-------------------------------------------+----------+
    | processor |  vendor_id   | cpu_family | model | stepping |                 model_name                | cpu_mhz  |
    +-----------+--------------+------------+-------+----------+-------------------------------------------+----------+
    |     0     | GenuineIntel |     6      |   62  |    4     | Intel(R) Xeon(R) CPU E5-1607 v2 @ 3.00GHz | 1200.000 |
    |     1     | GenuineIntel |     6      |   62  |    4     | Intel(R) Xeon(R) CPU E5-1607 v2 @ 3.00GHz | 2200.000 |
    |     2     | GenuineIntel |     6      |   62  |    4     | Intel(R) Xeon(R) CPU E5-1607 v2 @ 3.00GHz | 1200.000 |
    |     3     | GenuineIntel |     6      |   62  |    4     | Intel(R) Xeon(R) CPU E5-1607 v2 @ 3.00GHz | 2800.000 |
    +-----------+--------------+------------+-------+----------+-------------------------------------------+----------+

    Ethernet Controller Info:

    +---------------+-------------------+-----------+------------------------------------+-----------+----------------+--------------+----------------+--------------+
    | device_bus_id |    vendor_name    | vendor_id |            device_name             | device_id | subvendor_name | subvendor_id | subdevice_name | subdevice_id |
    +---------------+-------------------+-----------+------------------------------------+-----------+----------------+--------------+----------------+--------------+
    |    02:00.0    | Intel Corporation |    8086   | 82579LM Gigabit Network Connection |    1502   |      Dell      |     1028     | [Device 05d2]  |     05d2     |
    +---------------+-------------------+-----------+------------------------------------+-----------+----------------+--------------+----------------+--------------+

    Storage Controller Info:

    +-------------------+-----------+----------------------------------------------+-----------+----------------+--------------+----------------+--------------+
    |    vendor_name    | vendor_id |                 device_name                  | device_id | subvendor_name | subvendor_id | subdevice_name | subdevice_id |
    +-------------------+-----------+----------------------------------------------+-----------+----------------+--------------+----------------+--------------+
    | Intel Corporation |    8086   |   C600/X79 series chipset IDE-r Controller   |    1d3c   |      Dell      |     1028     | [Device 05d2]  |     05d2     |
    | Intel Corporation |    8086   | C600/X79 series chipset SATA RAID Controller |    2826   |      Dell      |     1028     | [Device 05d2]  |     05d2     |
    +-------------------+-----------+----------------------------------------------+-----------+----------------+--------------+----------------+--------------+

    GPU Info:

    +--------------------+-----------+-----------------------+-----------+--------------------+--------------+----------------+--------------+
    |    vendor_name     | vendor_id |      device_name      | device_id |   subvendor_name   | subvendor_id | subdevice_name | subdevice_id |
    +--------------------+-----------+-----------------------+-----------+--------------------+--------------+----------------+--------------+
    | NVIDIA Corporation |    10de   | GK107GL [Quadro K600] |    0ffa   | NVIDIA Corporation |     10de     | [Device 094b]  |     094b     |
    +--------------------+-----------+-----------------------+-----------+--------------------+--------------+----------------+--------------+

_Note: you may need to execute `hwinfo` with sudo depending on your systems permissions._

For remote executions you must provide a machine address, username and password:

    $> hwinfo -m 10.80.100.152 -u root -p password

If you have the captured outputs of the following:
    * /proc/cpuinfo as 'cpuinfo'
    * dmidecode as 'dmidecode.out'
    * lspci -nnm as 'lspci-nnm.out'

Then you can run `hwinfo` on that data in the following way:

    $> hwinfo -f <path to directory containing files>


Reporting Issues
----------------
This library is currently regarded as being in beta and so bugs are to be fully expected.
If you encounter any, please [report them](https://github.com/rdobson/python-hwinfo).

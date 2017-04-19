import unittest
import mock
import sys
from mock import patch
from StringIO import StringIO

from hwinfo.tools import inspector
import dummy_data

class HostMock(inspector.Host):

    def get_lspci_data(self):
        return dummy_data.LSPCI_DUMMY

    def get_dmidecode_data(self):
        return dummy_data.DMIDECODE_DUMMY

    def get_cpuinfo_data(self):
        return dummy_data.CPUINFO_DUMMY

    def get_os_data(self):
        return dummy_data.OS_DUMMY

class HostObjectTests(unittest.TestCase):

    @patch('hwinfo.tools.inspector.local_command')
    def test_local_exec_command(self, local_command):
        host = inspector.Host()
        host.exec_command('ls')
        inspector.local_command.assert_called_once_with('ls')

    @patch('hwinfo.tools.inspector.get_ssh_client')
    @patch('hwinfo.tools.inspector.remote_command')
    def test_remote_exec_command(self, remote_command, get_ssh_client):
        mclient = get_ssh_client.return_value = mock.MagicMock()
        host = inspector.Host('mymachine', 'root', 'pass')
        host.exec_command('ls')
        inspector.remote_command.assert_called_once_with(mclient, 'ls')

    @patch('hwinfo.tools.inspector.Host.exec_command')
    def test_get_pci_devices(self, exec_command):
        host = inspector.Host()
        devs = host.get_pci_devices()
        exec_command.assert_called_once_with(['lspci', '-nnmm'])

    @patch('hwinfo.host.dmidecode.DmidecodeParser')
    @patch('hwinfo.tools.inspector.Host.exec_command')
    def test_get_info(self, mock_exec_command, mock_dmidecode_parser_cls):
        mock_exec_command.return_value = 'blah'
        mparser = mock_dmidecode_parser_cls.return_value = mock.Mock()
        mparser.parse.return_value = {'key':'value'}
        host = inspector.Host()
        rec = host.get_info()
        self.assertEqual(rec, {'key':'value'})

    def test_is_not_remote(self):
        host = inspector.Host()
        self.assertEqual(host.is_remote(), False)

    @patch('hwinfo.tools.inspector.get_ssh_client')
    def test_is_remote(self, get_ssh_client):
        get_ssh_client.return_value = mock.MagicMock()
        host = inspector.Host('test', 'user', 'pass')
        self.assertEqual(host.is_remote(), True)


class HostFromTarballTests(unittest.TestCase):

    @patch('hwinfo.tools.inspector.find_in_tarball')
    @patch('hwinfo.tools.inspector.read_from_tarball')
    def test__load_from_file(self, read_from_tarball, find_in_tarball):
        tarball_name = 'test.tar.gz'
        filename = 'foobar.txt'
        filepath = find_in_tarball.return_value = \
            'somedir/anotherdir/%s' % filename

        host = inspector.HostFromTarball('test.tar.gz', preload=False)
        host._load_from_file(filename)

        find_in_tarball.assert_called_once_with(tarball_name, filename)
        read_from_tarball.assert_called_once_with(tarball_name, filepath)

class UtilTests(unittest.TestCase):

    @patch('tarfile.open')
    def test_find_in_tarball(self, tar_open):
        mtarfh = tar_open.return_value = mock.MagicMock()
        filename = 'foo.bar'
        filepath = 'testing/path/%s' % filename

        paths = [filepath, 'something/else/foo.pdf', 'extra/file.bin']

        mtar_infos = []
        for p in paths:
            m = mock.MagicMock()
            m.name = p
            mtar_infos.append(m)

        mtarfh.getmembers.return_value = mtar_infos

        path = inspector.find_in_tarball(mtarfh, filename)
        self.assertEqual(filepath, path)


    @patch('hwinfo.tools.inspector.read_from_file')
    @patch('tarfile.open')
    def test_read_from_tarball(self, tar_open, read_from_file):
        mtarfh = tar_open.return_value = mock.MagicMock()
        filepath = 'something/else/foo.pdf'

        mread = read_from_file.return_value = 'blah blah blah'

        data = inspector.read_from_tarball('testtar.tar.gz', filepath)
        self.assertEqual(mread, data)


class RemoteCommandTests(unittest.TestCase):

    def setUp(self):
        self.stdout = StringIO('')
        self.stdin = StringIO('')
        self.stderr = StringIO('')

    @patch('paramiko.SSHClient')
    def test_ssh_connect(self, ssh_client_cls):
        client = ssh_client_cls.return_value = mock.Mock()
        client.exec_command.return_value = self.stdout, self.stdin, self.stderr
        inspector.get_ssh_client('test', 'user', 'pass')
        client.connect.assert_called_with('test', password='pass', username='user', timeout=10)

    @patch('paramiko.SSHClient')
    def test_ssh_connect_error(self, ssh_client_cls):
        client = ssh_client_cls.return_value = mock.Mock()
        client.exec_command.return_value = self.stdout, self.stdin, StringIO("Error")
        with self.assertRaises(Exception) as context:
            inspector.remote_command(client, 'ls')
        self.assertEqual(context.exception.message, "stderr: ['Error']")

class LocalCommandTests(unittest.TestCase):

    @patch('subprocess.Popen')
    def test_local_call(self, mock_popen_cls):
        mprocess =mock_popen_cls.return_value = mock.MagicMock()
        mprocess.communicate.return_value = 'test', None
        mprocess.returncode = 0
        stdout = inspector.local_command("echo 'test'")
        self.assertEqual(stdout, 'test')

    @patch('subprocess.Popen')
    def test_local_call_error(self, mock_popen_cls):
        mprocess =mock_popen_cls.return_value = mock.MagicMock()
        mprocess.communicate.return_value = 'test', 'my error'
        mprocess.returncode = 1
        with self.assertRaises(Exception) as context:
            stdout = inspector.local_command("echo 'test'")
        self.assertEqual(context.exception.message, "stderr: my error")


class PCIFilterTests(unittest.TestCase):

    def setUp(self):
        device_a = mock.MagicMock()
        device_b = mock.MagicMock()
        device_c = mock.MagicMock()
        device_d = mock.MagicMock()
        device_e = mock.MagicMock()

        device_a.get_pci_class.return_value = '0230'
        device_b.get_pci_class.return_value = '0340'
        device_c.get_pci_class.return_value = '0210'
        device_d.get_pci_class.return_value = '0100'
        device_e.get_pci_class.return_value = '0c04'

        self.devices = [device_a, device_b, device_c, device_d, device_e]

    def test_pci_filter_match_all(self):
        devs = inspector.pci_filter(self.devices, ['0'])
        self.assertEqual(len(devs), len(self.devices))

    def test_pci_filter_match_two(self):
        devs = inspector.pci_filter(self.devices, ['02'])
        for dev in devs:
            print dev.get_pci_class()
        self.assertEqual(len(devs), 2)

    def test_pci_filter_match_one(self):
        devs = inspector.pci_filter(self.devices, ['023'])
        self.assertEqual(len(devs), 1)
        self.assertEqual(devs[0].get_pci_class(), '0230')

    def test_pci_filter_match_none(self):
        devs = inspector.pci_filter(self.devices, ['0234'])
        self.assertEqual(devs, [])

    def test_pci_filter_for_nics(self):
        devs = inspector.pci_filter_for_nics(self.devices)
        self.assertEqual(len(devs), 2)

    def test_pci_filter_for_storage(self):
        devs = inspector.pci_filter_for_storage(self.devices)
        self.assertEqual(len(devs), 2)

    def test_pci_filter_for_gpu(self):
        devs = inspector.pci_filter_for_gpu(self.devices)
        self.assertEqual(len(devs), 1)
        self.assertEqual(devs[0].get_pci_class(), '0340')


class TabulateTests(unittest.TestCase):

    @patch('hwinfo.tools.inspector.PrettyTable')
    def test_rec_to_table(self, mock_pt_cls):
        mock_table = mock_pt_cls.return_value = mock.MagicMock()
        rec = {'one': 1, 'two': 2, 'three': 3}
        inspector.rec_to_table(rec)
        self.assertEqual(mock_table.add_row.call_count, 3)
        expected_calls = [
            mock.call(['one', 1]),
            mock.call(['two', 2]),
            mock.call(['three', 3]),
        ]
        mock_table.add_row.assert_has_calls(expected_calls, any_order=True)

class CombineRecsTests(unittest.TestCase):


    def _validate_rec(self, rec, key, value):
        self.assertEqual(rec[key], value)

    def test_combine_two_recs(self):
        recs = [
            {
                'name':'rec1',
                'valuea': '10',
                'valueb': '11',
                'valuec': '12',
            },
            {
                'name': 'rec1',
                'valued': '5',
                'valuee': '8',
            },
        ]

        combined_recs = inspector.combine_recs(recs, 'name')
        self.assertEqual(len(combined_recs), 1)
        rec = combined_recs[0]
        self._validate_rec(rec, 'valuea', '10')
        self._validate_rec(rec, 'valueb', '11')
        self._validate_rec(rec, 'valuec', '12')
        self._validate_rec(rec, 'valued', '5')
        self._validate_rec(rec, 'valuee', '8')

    def test_combine_three_recs(self):
        recs = [
            {
                'name':'rec1',
                'valuea': '10',
                'valueb': '11',
                'valuec': '12',
            },
            {
                'name': 'rec1',
                'valued': '5',
                'valuee': '8',
            },
            {
                'name': 'rec1',
                'valuef': '1',
                'valueg': '2',
            },
        ]

        combined_recs = inspector.combine_recs(recs, 'name')
        self.assertEqual(len(combined_recs), 1)
        rec = combined_recs[0]
        self._validate_rec(rec, 'valuea', '10')
        self._validate_rec(rec, 'valueb', '11')
        self._validate_rec(rec, 'valuec', '12')
        self._validate_rec(rec, 'valued', '5')
        self._validate_rec(rec, 'valuee', '8')
        self._validate_rec(rec, 'valuef', '1')
        self._validate_rec(rec, 'valueg', '2')

    def test_combine_three_recs_to_two(self):
        recs = [
            {
                'name':'rec1',
                'valuea': '10',
                'valueb': '11',
                'valuec': '12',
            },
            {
                'name': 'rec2',
                'valued': '5',
                'valuee': '8',
            },
            {
                'name': 'rec1',
                'valuef': '1',
                'valueg': '2',
            },
        ]

        combined_recs = inspector.combine_recs(recs, 'name')
        self.assertEqual(len(combined_recs), 2)
        for rec in combined_recs:
            if rec['name'] == 'rec1':
                self._validate_rec(rec, 'valuea', '10')
                self._validate_rec(rec, 'valueb', '11')
                self._validate_rec(rec, 'valuec', '12')
                self._validate_rec(rec, 'valuef', '1')
                self._validate_rec(rec, 'valueg', '2')
            elif rec['name'] == 'rec2':
                self._validate_rec(rec, 'valued', '5')
                self._validate_rec(rec, 'valuee', '8')
            else:
                raise Exception("Unexpected rec: %s" % rec)

    def test_colliding_values(self):
        recs = [
            {
                'name':'rec1',
                'valuea': '10',
                'valueb': '11',
                'valuec': '12',
            },
            {
                'name': 'rec1',
                'valuea': '5',
                'valuee': '8',
            },
        ]
        with self.assertRaises(Exception) as context:
            combined_recs = inspector.combine_recs(recs, 'name')
        self.assertEqual(context.exception.message, "Mis-match for key 'valuea'")


class CLITests(unittest.TestCase):

    OPTIONS = ['bios', 'nic', 'storage', 'gpu', 'cpu']

    @patch('hwinfo.tools.inspector.system_info')
    @patch('hwinfo.tools.inspector.Host')
    @patch('sys.argv')
    def test_local_machine(self, argv, host_cls, system_info):
        argv = ['hwinfo']
        mhost = host_cls.return_value = mock.MagicMock()
        inspector.main()
        host_cls.assert_called_with('localhost',None, None)
        system_info.assert_called_with(mhost, self.OPTIONS)

    @patch('hwinfo.tools.inspector.system_info')
    @patch('hwinfo.tools.inspector.Host')
    def test_remote_machine(self, host_cls, system_info):
        sys.argv = ['hwinfo', '-m', 'test', '-u', 'root', '-p', 'pass']
        mhost = host_cls.return_value = mock.MagicMock()
        inspector.main()
        host_cls.assert_called_with('test', 'root' , 'pass')
        system_info.assert_called_with(mhost, self.OPTIONS)

    @patch('hwinfo.tools.inspector.system_info')
    @patch('hwinfo.tools.inspector.HostFromLogs')
    def test_host_from_logs(self, host_cls, system_info):
        sys.argv = ['hwinfo', '-l', '/tmp/thisisatestpath']
        mhost = host_cls.return_value = mock.MagicMock()
        inspector.main()
        host_cls.assert_called_with('/tmp/thisisatestpath')
        system_info.assert_called_with(mhost, self.OPTIONS)

    @patch('hwinfo.tools.inspector.system_info')
    @patch('hwinfo.tools.inspector.Host')
    def test_local_machine_filter_for_nic(self, host_cls, system_info):
        sys.argv = ['hwinfo', '-f', 'nic']
        mhost = host_cls.return_value = mock.MagicMock()
        inspector.main()
        system_info.assert_called_with(mhost, ['nic'])

    @patch('hwinfo.tools.inspector.system_info')
    @patch('hwinfo.tools.inspector.Host')
    def test_local_machine_filter_for_gpu(self, host_cls, system_info):
        sys.argv = ['hwinfo', '-f', 'gpu']
        mhost = host_cls.return_value = mock.MagicMock()
        inspector.main()
        system_info.assert_called_with(mhost, ['gpu'])

    @patch('hwinfo.tools.inspector.export_system_info')
    @patch('hwinfo.tools.inspector.Host')
    def test_export(self, host_cls, export_system_info):
        sys.argv = ['hwinfo', '-e']
        mhost = host_cls.return_value = mock.MagicMock()
        inspector.main()
        export_system_info.assert_called_with(mhost, self.OPTIONS)

    @patch('sys.exit')
    def test_validate_args_no_username(self, exit):
        args = mock.MagicMock()
        args.machine = 'test'
        args.username = None
        args.password = 'test'
        inspector.validate_args(args)
        exit.assert_called_with(1)

    @patch('sys.exit')
    def test_validate_args_no_password(self, exit):
        args = mock.MagicMock()
        args.machine = 'test'
        args.username = 'user'
        args.password = None
        inspector.validate_args(args)
        exit.assert_called_with(1)

    def test_validate_local_machine(self):
        args = mock.MagicMock()
        args.machine = 'localhost'
        args.username = None
        args.password = None
        inspector.validate_args(args)

    @patch('hwinfo.tools.inspector.system_info')
    @patch('hwinfo.tools.inspector.HostFromTarball')
    def test_from_tarball(self, host_cls, system_info):
        sys.argv = ['hwinfo', '-l', 'ack-submission.tar.gz']
        mhost = host_cls.return_value = mock.MagicMock()
        inspector.main()
        host_cls.assert_called_with('ack-submission.tar.gz')

class SystemInfoTests(unittest.TestCase):

    def test_print_all(self):
        mhost =  HostMock()
        options = ['bios', 'nic', 'storage', 'gpu', 'cpu']
        out = inspector.system_info(mhost, options)
        self.assertEqual(len(out.split(" Info:\n\n")), 6)

    def test_print_bios(self):
        mhost =  HostMock()
        options = ['bios']
        out = inspector.system_info(mhost, options)
        self.assertEqual(len(out.split(" Info:\n\n")), 2)

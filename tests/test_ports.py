import os
import sys
import unittest

from models.port import Port
from models.port_group import PortGroup

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))
pparent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))
# Add the parent directory to sys.path
sys.path.append(pparent_dir)

class TestPorts(unittest.TestCase):
    def test_port_size(self):
        test_ports = [
                        {"value": Port('1', 'test_port1', 'TCP', '80'), "result": 1} ,
                        {"value": Port('2', 'test_port2', 'TCP', '80-81'), "result": 2},
                        {"value": Port('3', 'test_port3', 'TCP', '1000 - 1101'), "result": 102}
        ]

        for testcase in test_ports:
            testcase['value'].calculate_protocol_port_object_size()
            self.assertEqual(testcase['value'].size, testcase["result"])

    def test_is_risky(self):
        test_ports = [
                        {"value": Port('1', 'test_port1', 'TCP', '80'), "result": True} ,
                        {"value": Port('2', 'test_port2', 'TCP', '21'), "result": True},
                        {"value": Port('3', 'test_port3', 'TCP', '443'), "result": False},
        ]
        config = {'HIGH_RISK_PROTOCOLS': {'TCP': [20, 21, 23, 80, 5800, 5900, 8080], 'UDP': [69], 'ICMP': []}}

        for testcase in test_ports:
            is_risky = testcase['value']._is_risky_port(config['HIGH_RISK_PROTOCOLS'])
            self.assertEqual(is_risky, testcase["result"])

    def test_flat_port_group(self):
        port_group = PortGroup('1', 'test_grp')
        port_group_1 = PortGroup('2', 'test_grp2')
        port_group_1.ports.append(Port('1', 'test1', 'TCP', '80'))
        port_group_1.ports.append(Port('2', 'test2', 'TCP', '21'))
        port_group.ports.append(port_group_1)
        test_ports = [
                        {"value": port_group, "result": port_group_1.ports}
        ]

        for testcase in test_ports:
            final = testcase['value'].flat_port_object_grp()
            self.assertEqual(final, testcase["result"])

if __name__ == "__main__":
    unittest.main()

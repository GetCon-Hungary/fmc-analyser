import sys
import os
import unittest

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))
pparent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))
# Add the parent directory to sys.path
sys.path.append(pparent_dir)

from Models.Network import Network
from Models.NetworkGroup import NetworkGroup

class TestNetworks(unittest.TestCase):

    def test_network_size(self):
        network0 = Network('1', 'Range', 'test_0', '192.168.0.1-192.168.0.5')
        network1 = Network('2', 'Range', 'test_1', '192.168.0.1-192.168.1.1')
        network2 = Network('3', 'Network', 'test_2', '192.168.0.0/24')
        network3 = Network('4', 'Network', 'test_3', '192.168.0.0/27')
        network4 = Network('5', 'Network', 'test_4', '192.168.0.0/16')
        test_networks = [
                        {"value": network0, "result": 5},
                        {"value": network1, "result": 257},
                        {"value": network2, "result": 256},
                        {"value": network3, "result": 32}, 
                        {"value": network4, "result": 65536} 
        ]

        for testcase in test_networks:
            self.assertEqual(testcase['value'].size, testcase["result"])
    
    def test_flat_network_group(self):
        network_group = NetworkGroup('1', 'test_grp')
        network_group_1 = NetworkGroup('2', 'test_grp2')
        network_group_2 = NetworkGroup('3', 'test_grp3')

        network_group_1.networks.append(Network('1', 'Host', 'test_network_1', '10.10.10.10'))
        network_group_1.networks.append(Network('2', 'Network', 'test_network_2', '10.10.10.0/24'))
        network_group_2.networks.append(Network('3', 'Range', 'test_network_3', '192.168.0.1-192.168.0.5'))
        network_group_2.networks.append(Network('4', 'Network', 'test_network_4', '192.168.0.0/27'))

        network_group.networks.append(network_group_1)
        network_group.networks.append(network_group_2)
        result_network = network_group_1.networks + network_group_2.networks

        test_networks = [
                        {"value": network_group, "result": result_network}
        ]

        for testcase in test_networks:
            final = testcase['value'].flat_network_object_grp()
            self.assertEqual(final, testcase["result"])

    def test_network_depth(self):
        network_group = NetworkGroup('1', 'test_grp')
        network_group_1 = NetworkGroup('2', 'test_grp2')
        network_group_2 = NetworkGroup('3', 'test_grp3')

        network_group_1.networks.append(network_group_2)
        network_group.networks.append(network_group_1)

        test_networks = [
                        {"value": network_group, "result": 2},
        ]

        for testcase in test_networks:
            depth = testcase['value'].get_network_depth()
            self.assertEqual(depth, testcase["result"])

if __name__ == "__main__":
    unittest.main()
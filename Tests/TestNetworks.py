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
        network = Network(None, None, None)
        test_networks = [
                        {"value": "192.168.0.1 - 192.168.0.5", "result": 5},
                        {"value": "192.168.0.1 - 192.168.1.1", "result": 257},
                        {"value": "192.168.0.0/24", "result": 256},
                        {"value": "192.168.0.0/27", "result": 32}, 
                        {"value": "192.168.0.0/16", "result": 65536} 
        ]

        for testcase in test_networks:
            network.calculate_network_size(testcase)
            self.assertEqual(network.size, testcase["result"])
    
    def test_flat_network_group(self):
        network_group = NetworkGroup('1', 'test_grp')
        network_group_1 = NetworkGroup('2', 'test_grp2')
        network_group_2 = NetworkGroup('3', 'test_grp3')

        network_group_1.networks.append(Network('1', 'Host', 'test_network_1'))
        network_group_1.networks.append(Network('2', 'Network', 'test_network_2'))
        network_group_2.networks.append(Network('3', 'Range', 'test_network_3'))
        network_group_2.networks.append(Network('4', 'Network', 'test_network_4'))

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
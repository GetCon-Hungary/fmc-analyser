import sys
import os

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))
pparent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))
# Add the parent directory to sys.path
sys.path.append(pparent_dir)

import Main

def test_range_size():
    test_ranges = [
                    {"value": "192.168.0.1 - 192.168.0.5", "result": 5} ,
                    {"value": "192.168.0.1 - 192.168.1.1", "result": 257} 
    ]

    for testcase in test_ranges:
        network, size = Main.calculate_range_size(testcase)
        assert size == testcase["result"]

def test_network_size():
    test_networks = [
                    {"value": "192.168.0.0/24", "result": 256} ,
                    {"value": "192.168.0.0/27", "result": 32}, 
                    {"value": "192.168.0.0/16", "result": 65536} 
    ]

    for testcase in test_networks:
        network, size = Main.calculate_network_size(testcase)
        assert size == testcase["result"]

def test_port_size():
    test_ports = [
                    {"value": "80", "result": 1} ,
                    {"value": "80-81", "result": 2}, 
                    {"value": "1000 - 1101", "result": 101} 
    ]

    for testcase in test_ports:
        size = Main.calculate_protocol_port_object_size(testcase["value"])
        assert size == testcase["result"]


if __name__ == "__main__":
    test_port_size()
    test_range_size()
    test_network_size()



import sys
import os
import unittest

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))
pparent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))
# Add the parent directory to sys.path
sys.path.append(pparent_dir)

from Models.Network import Network
from Models.Port import Port
from Models.PortGroup import PortGroup
from Models.AccessRule import AccessRule

class TestAccessRules(unittest.TestCase):

    def setUp(self) -> None:
        self.rule1 = AccessRule('1', 'test_rule1', 'allow', True)
        self.rule2 = AccessRule('2', 'test_rule2', 'allow', True)
        self.rule3 = AccessRule('3', 'test_rule3', 'allow', True)
        self.rule4 = AccessRule('4', 'test_rule4', 'allow', True)
        self.rule5 = AccessRule('5', 'test_rule5', 'allow', True)
        self.rule6 = AccessRule('6', 'test_rule6', 'allow', True)
        self.rule7 = AccessRule('7', 'test_rule7', 'allow', True)
        self.rule8 = AccessRule('8', 'test_rule8', 'allow', True)
    

    def test_risk_category_by_port(self):
        self.create_ports_for_test()
        test_networks = [
                        {"value": self.rule1, "result": 'High'},
                        {"value": self.rule2, "result": 'High'},
                        {"value": self.rule3, "result": 'Medium'},
                        {"value": self.rule4, "result": 'Low'},
                        {"value": self.rule5, "result": 'Low'},
                        {"value": self.rule6, "result": 'High'},
                        {"value": self.rule7, "result": 'Medium'},
                        {"value": self.rule8, "result": 'Low'},
        ]

        for testcase in test_networks:
            risk = testcase['value'].risk_category_by_port()
            self.assertEqual(risk, testcase["result"])
    
    def create_ports_for_test(self):
        self.port_group = PortGroup('1', 'test_group')
        self.port_group2 = PortGroup('2', 'test_group2')
        self.port_group3 = PortGroup('3', 'test_group3')

        for i in range(11):
            self.rule2.destination_ports.append(Port(str(i), 'test_port{}'.format(i), 'TCP', str(i)))
            self.port_group.ports.append(Port(str(i), 'test_port{}'.format(i), 'TCP', str(i)))
        for i in range(6):
            self.rule3.destination_ports.append(Port(str(i), 'test_port{}'.format(i), 'TCP', str(i)))
            self.port_group2.ports.append(Port(str(i), 'test_port{}'.format(i), 'TCP', str(i)))
        for i in range(5):
            self.rule4.destination_ports.append(Port(str(i), 'test_port{}'.format(i), 'TCP', str(i)))
            self.port_group3.ports.append(Port(str(i), 'test_port{}'.format(i), 'TCP', str(i)))
            
        self.rule5.destination_ports.append(Port('1', 'test_port', 'TCP', '20'))
        self.rule6.destination_ports.append(self.port_group)
        self.rule7.destination_ports.append(self.port_group2)
        self.rule8.destination_ports.append(self.port_group3)

if __name__ == "__main__":
    unittest.main()
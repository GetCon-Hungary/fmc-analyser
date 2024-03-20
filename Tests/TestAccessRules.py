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
        ports = self.create_ports_for_test()
        port_grp = self.create_port_groups_for_test(ports)

        self.rule0 = AccessRule(id='0', name='test_rule0', action='allow', enabled='True', source_networks=[], source_zones=['Inside'], source_ports=[], destination_networks=[], destination_zones=['OUTISDE'], destination_ports=[])
        self.rule1 = AccessRule(id='1', name='test_rule1', action='allow', enabled='True', source_networks=[], source_zones=['Inside'], source_ports=[], destination_networks=[], destination_zones=['OUTISDE'], destination_ports=ports['rule1'])
        self.rule2 = AccessRule(id='2', name='test_rule2', action='allow', enabled='True', source_networks=[], source_zones=['Inside'], source_ports=[], destination_networks=[], destination_zones=['OUTISDE'], destination_ports=ports['rule2'])
        self.rule3 = AccessRule(id='3', name='test_rule3', action='allow', enabled='True', source_networks=[], source_zones=['Inside'], source_ports=[], destination_networks=[], destination_zones=['OUTISDE'], destination_ports=ports['rule3'])
        self.rule4 = AccessRule(id='4', name='test_rule4', action='allow', enabled='True', source_networks=[], source_zones=['Inside'], source_ports=[], destination_networks=[], destination_zones=['OUTISDE'], destination_ports=[Port('1', 'test_port', 'TCP', '20')])
        self.rule5 = AccessRule(id='5', name='test_rule5', action='allow', enabled='True', source_networks=[], source_zones=['Inside'], source_ports=[], destination_networks=[], destination_zones=['OUTISDE'], destination_ports=[port_grp[0]])
        self.rule6 = AccessRule(id='6', name='test_rule6', action='allow', enabled='True', source_networks=[], source_zones=['Inside'], source_ports=[], destination_networks=[], destination_zones=['OUTISDE'], destination_ports=[port_grp[1]])
        self.rule7 = AccessRule(id='7', name='test_rule7', action='allow', enabled='True', source_networks=[], source_zones=['Inside'], source_ports=[], destination_networks=[], destination_zones=['OUTISDE'], destination_ports=[port_grp[2]])
        
    

    def test_risk_category_by_port_static(self):
        test_networks = [
                        {"value": self.rule0, "result": 'High'},
                        {"value": self.rule1, "result": 'High'},
                        {"value": self.rule2, "result": 'Medium'},
                        {"value": self.rule3, "result": 'Low'},
                        {"value": self.rule4, "result": 'Low'},
                        {"value": self.rule5, "result": 'High'},
                        {"value": self.rule6, "result": 'Medium'},
                        {"value": self.rule7, "result": 'Low'},
        ]

        config = {'DESTINATION_PORT_CATEGORIES': {'HIGH': 16, 'MEDIUM': 8, 'LOW': 4}}

        for testcase in test_networks:
            risk = testcase['value'].risk_category_by_destination_port_static(config['DESTINATION_PORT_CATEGORIES'])
            self.assertEqual(risk, testcase["result"])
    
    def test_risk_category_by_port_dynamic(self):
        test_networks = [
                        {"value": self.rule0, "result": 'High'},
                        {"value": self.rule1, "result": 'Medium'},
                        {"value": self.rule2, "result": 'Low'},
        ]

        config = {'RELATIVE_DESTINATION_PORT_CATEGORIES': {'HIGH': 10, 'MEDIUM': 5, 'LOW': 3}}

        for testcase in test_networks:
            if isinstance(testcase['value'], AccessRule):
                risk = testcase['value'].risk_category_by_destination_port_dynamic(2, config['RELATIVE_DESTINATION_PORT_CATEGORIES'])
            self.assertEqual(risk, testcase["result"])
    
    def create_ports_for_test(self):
        ports_dict: dict[str, list] = {}
        ports = []
        for i in range(16):
            ports.append(Port(str(i), 'test_port{}'.format(i), 'TCP', str(i))) 
        ports_dict['rule1'] = ports
        ports_dict['group0'] = ports
        ports = []
        for i in range(8):
            ports.append(Port(str(i), 'test_port{}'.format(i), 'TCP', str(i))) 
        ports_dict['rule2'] = ports
        ports_dict['group1'] = ports
        ports = []
        for i in range(5):
            ports.append(Port(str(i), 'test_port{}'.format(i), 'TCP', str(i))) 
        ports_dict['rule3'] = ports
        ports_dict['group2'] = ports
        
        return ports_dict

    def create_networks_for_test(self):
        pass

    def create_port_groups_for_test(self, ports):
        port_grps = []
        for i in range(3):
            grp = PortGroup(i, 'test_group_{}'.format(i))
            grp.ports.extend(ports['group{}'.format(i)])
            port_grps.append(grp)
        return port_grps

if __name__ == "__main__":
    unittest.main()
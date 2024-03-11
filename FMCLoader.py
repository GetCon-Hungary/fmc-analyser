import fmcapi
import logging
from Models.Port import Port


def convert_port_objects(ports):
    result = {}
    for item in ports['items']:
        id = item.get('id', None)
        name = item.get('name', None)
        type = item.get('type', None)
        port = None
        protocol = None
        if type == 'ProtocolPortObject':
            port = item.get('port', None)
            protocol = item.get('protocol', None)
        elif type == 'ICMPV4Object':
            protocol = 'ICMPv4'
        else:
            raise TypeError('Only TCP, UDP and ICMPv4 supported')
        #ToDo: size -> size() function, is_risky -> is_risky() function
        port_obj = Port(id, name, protocol, port, 0,  False)
        result[name] = port_obj
        logging.info(f'PortProtocolObject: Name: {name} - protocol: {protocol} - type: {type} - port: {port}')
    return result


def convert_port_groups(portgroups, ports):
    result = {}
    for item in portgroups['items']:
        name = item.get('name', None)
        child_ports = []
        for object in item['objects']:
            port = ports.get(object['name'],None)
            if port:
                child_ports.append(port)
            else:
                raise NameError(f'{object[name]} not found')
        result[name] = child_ports
    return result
    

def convert_networks(networks):
    result = {}
    for item in networks['items']:
        print(item)


def convert_network_groups(network_groups, networks):
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    result = {}
    for item in network_groups['items']:
        print(item)


def convert_access_policy(access_policy):
    print('test')


def get_access_policy_rules(fmc, acp):
        policies = {}
        for acp in acp['items']:
            id = acp.get('id', None)
            name = acp.get('name', None)
            accessrules = fmcapi.AccessRules(fmc, acp_id=id).get()
            policies['name'] = accessrules
        return policies


class FMCLoader():
    def __init__(self, fmc_host, username, password):
        with fmcapi.FMC(fmc_host,username=username, password=password, autodeploy=False) as fmc:
            
            
            self.ports = convert_port_objects(fmcapi.Ports(fmc).get())
            self.port_object_groups = convert_port_groups(fmcapi.PortObjectGroups(fmc).get(),self.ports)
            self.networks = convert_networks(fmcapi.Networks(fmc).get())
            self.network_groups = convert_network_groups(fmcapi.NetworkGroups(fmc).get(),self.networks)
            self.ranges = fmcapi.Ranges(fmc).get()
            self.hosts = fmcapi.Hosts(fmc).get()

            self.acp = fmcapi.AccessPolicies(fmc).get()
            get_access_policy_rules(fmc,self.acp)            

            self.security_zones = fmcapi.SecurityZones(fmc).get()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    fmcloader = FMCLoader('192.168.33.193', 'farkas.balazs', 'Alma123!!')
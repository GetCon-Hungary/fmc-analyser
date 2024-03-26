"""Gets all the necessary data from FMC."""
import fmcapi


class FMCLoader:
    def __init__(self, fmc_host: str, username: str, password: str, acp_name: str) -> None:
        with fmcapi.FMC(fmc_host,username=username, password=password, autodeploy=False) as fmc:
            self.protocol_port_objs = fmcapi.ProtocolPortObjects(fmc).get()
            self.port_obj_groups = fmcapi.PortObjectGroups(fmc).get()
            self.networks = self.get_networks(fmc)
            self.network_groups = fmcapi.NetworkGroups(fmc).get()
            self.access_policies = self.get_access_policies(fmc, acp_name)
            self.access_rules = self.get_access_rules(fmc)
    
    def get_networks(self, fmc):
        networks: dict[str, list] = {'items': []}
        hosts = fmcapi.Hosts(fmc).get()
        networks_ = fmcapi.Networks(fmc).get()
        ranges = fmcapi.Ranges(fmc).get()
        networks['items'].extend(hosts['items'])
        networks['items'].extend(networks_['items'])
        networks['items'].extend(ranges['items'])
        return networks

    def get_access_policies(self, fmc: fmcapi.FMC, acp_name: str) -> dict:
        access_policies = {}
        if acp_name == 'all':
            access_policies = fmcapi.AccessPolicies(fmc).get()
            return access_policies
        policy = fmcapi.AccessPolicies(fmc, name=acp_name).get()
        if policy.get('id', None) is not None:
            access_policies['items'] = [policy]
            return access_policies
        raise NameError('Wrong access policy name')

    def get_access_rules(self, fmc: fmcapi.FMC) -> dict:
        access_rules = {}
        for access_policy in self.access_policies['items']:
            access_rules[access_policy['name']] = fmcapi.AccessRules(
                fmc, acp_id=access_policy['id']).get()
        return access_rules

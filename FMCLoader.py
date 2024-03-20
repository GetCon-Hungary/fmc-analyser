import fmcapi

class FMCLoader():
    def __init__(self, fmc_host: str, username: str, password: str, acp_name: str):
        with fmcapi.FMC(fmc_host,username=username, password=password, autodeploy=False) as fmc:

            self.protocol_port_objs = fmcapi.ProtocolPortObjects(fmc).get()
            self.port_obj_groups = fmcapi.PortObjectGroups(fmc).get()
            self.hosts = fmcapi.Hosts(fmc).get()
            self.networks = fmcapi.Networks(fmc).get()
            self.ranges = fmcapi.Ranges(fmc).get()
            self.network_groups = fmcapi.NetworkGroups(fmc).get()
            self.access_policies = self.get_acess_policies(fmc, acp_name)
            self.access_rules = self.get_acess_rules(fmc)
    
    def get_acess_policies(self, fmc, acp_name: str):
        access_policies = {}
        if acp_name == 'all':
            access_policies = fmcapi.AccessPolicies(fmc).get()
            return access_policies
        else:
            policy = fmcapi.AccessPolicies(fmc, name=acp_name).get()
            if policy.get('id', None) is not None:
                access_policies['items'] = [policy]
                return access_policies
            else:
                raise NameError('Wrong access policy name')
    
    def get_acess_rules(self, fmc):
        access_rules = {}
        for access_policy in self.access_policies['items']:
            access_rules[access_policy['name']] = fmcapi.AccessRules(fmc, acp_id=access_policy['id']).get()
        return access_rules
         

                
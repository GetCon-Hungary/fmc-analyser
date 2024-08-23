"""Gets all the necessary data from FMC."""
import fmcapi


class FMCLoader:
    def __init__(self, fmc_host: str, username: str, password: str, acp_name: str) -> None:  # noqa: D107
        with fmcapi.FMC(host=fmc_host, username=username, password=password, autodeploy=False, logging_level="NOTSET", timeout=60) as self.fmc:
            self.protocol_port_objs = fmcapi.ProtocolPortObjects(self.fmc).get()
            self.port_obj_groups = fmcapi.PortObjectGroups(self.fmc).get()
            self.networks = self.__get_networks()
            self.network_groups = fmcapi.NetworkGroups(self.fmc).get()
            self.access_policies = self.__get_access_policies(acp_name)
            self.access_rules = self.__get_access_rules()

    def __get_networks(self) -> dict[str, list]:
        """Get all the networks from FMC.

        Args:
        ----
            fmc (fmcapi.FMC): The FMC object used for query.

        Returns:
        -------
            dict[str, list]: The dict of networks.

        """
        networks: dict[str, list] = {'items': []}
        hosts = fmcapi.Hosts(self.fmc).get()
        networks_ = fmcapi.Networks(self.fmc).get()
        ranges = fmcapi.Ranges(self.fmc).get()
        networks['items'].extend(hosts['items'])
        networks['items'].extend(networks_['items'])
        networks['items'].extend(ranges['items'])
        return networks

    def __get_access_policies(self, acp_name: str) -> dict:
        """Get the specified access policy from FMC. If acp_name is "all" then get all the access policies from FMC

        Args:
        ----
            fmc (fmcapi.FMC): The FMC object used for query.

        Returns:
        -------
            dict: The dict of access policies.

        """
        access_policies = {}
        if acp_name == 'all':
            return fmcapi.AccessPolicies(self.fmc).get()
        policy = fmcapi.AccessPolicies(self.fmc, name=acp_name).get()
        if policy.get('id', None) is not None:
            access_policies['items'] = [policy]
            return access_policies
        raise NameError('Wrong access policy name')

    def __get_access_rules(self) -> dict:
        """Get the access rules of access policies from FMC.

        Args:
        ----
            fmc (fmcapi.FMC): The FMC object used for query.

        Returns:
        -------
            dict: The dict of access rules by policy names.

        """
        access_rules = {}
        for access_policy in self.access_policies['items']:
            access_rules[access_policy['name']] = fmcapi.AccessRules(
                self.fmc, acp_id=access_policy['id']).get()
        return access_rules
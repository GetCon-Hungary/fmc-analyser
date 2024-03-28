"""Where the magic happens."""
import argparse
import sys
import os

import logic.excel_export as exp
from logic.builder_logic import Builder
from logic.export_data_logic import Data
from logic.fmc_loader import FMCLoader

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='FMC Analyser')
        parser.add_argument('-H', '--host', required=True, help='IP address of FMC')
        parser.add_argument('-U', '--username', required=True, help='FMC login username')
        parser.add_argument('-P', '--password', required=True, help='FMC login password')
        parser.add_argument('-A', '--acp', required=False, default='all', help='Rule name you want to analyse. Leave blank for default "all"')
        parser.add_argument('-C', '--config', required=False, default='config.yml', help='Config file path. Leave blank for default: config.yml')

        ARGS = parser.parse_args()

        fmcloader = FMCLoader(ARGS.host, ARGS.username, ARGS.password, ARGS.acp)
    except FileNotFoundError:
        sys.stdout.write('File {} not found.'.format(ARGS.config))
    except:
        sys.stdout.write('Please do not forget the required command arguments: host, username and password')

    builder = Builder(fmcloader)
    data = Data(builder, ARGS.config)

    exp.export_to_excel(data.access_policies_data, exp.ACCESS_POLICY_HEADER, 'access_policies_information')
    for policy in builder.policies:
        exp.export_to_excel(
            data.access_rules_data[policy.name],
            exp.ACCESS_RULE_HEADER,
            'access_rules_of_{}'.format(policy.name),
        )
    exp.export_to_excel(data.ports_data, exp.PORTS_HEADER, 'ports')
    exp.export_to_excel(data.networks_data, exp.NETWORK_HEADER, 'networks')

    sys.stdout.write('Done')
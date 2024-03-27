"""Where the magic happens."""
import argparse
import sys

import logic.excel_export as exp
from config import settings
from logic.builder_logic import Builder
from logic.export_data_logic import Data
from logic.fmc_loader import FMCLoader

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='FMC Analyser')
        parser.add_argument('-h', '--host', required=True, help='IP address of FMC')
        parser.add_argument('-u', '--username', required=True, help='FMC login username')
        parser.add_argument('-p', '--password', required=True, help='FMC login password')
        parser.add_argument('-a', '--acp', required=False, choices=['acp', 'ports', 'networks'], default='all', help='chose from list or leave it blank and run all by default')
        parser.add_argument('-c', '--config', required=False, default='config.yml', help='Type config file or leave it blank for config.yml')

        ARGS = parser.parse_args()

        fmcloader = FMCLoader(ARGS.host, ARGS.username, ARGS.password, ARGS.acp)
    except FileNotFoundError:
        sys.stdout.write('File {} not found.'.format(ARGS.config))
    except:
        fmcloader = FMCLoader(settings.fmc_host, settings.fmc_user, settings.fmc_pass, 'all')

    builder = Builder(fmcloader)
    try:
        data = Data(builder, ARGS.config)
    except (NameError, AttributeError, FileNotFoundError):
        data = Data(builder, 'config.yml')

    exp.export_to_excel(data.access_policies_data, exp.ACCESS_POLICY_HEADER, 'access_policies_information')
    for policy in builder.policies:
        exp.export_to_excel(
            data.access_rules_data[policy.name],
            exp.ACCESS_RULE_HEADER,
            'access_rules_of_{}'.format(policy.name),
        )
    exp.export_to_excel(data.ports_data, exp.PORTS_HEADER, 'ports')
    exp.export_to_excel(data.networks_data, exp.NETWORK_HEADER, 'networks')

    print('Done')
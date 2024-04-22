"""Where the magic happens."""
import argparse
import sys
import openpyxl

from logic.fmc_loader import FMCLoader
from logic.builder_logic import Builder
from logic.export_data_logic import Data
from logic.excel_export import Export

if __name__ == "__main__":
    print('--- FMC Analyser ---')
    print('Getting data from FMC ... ', end='', flush=True)
    parser = argparse.ArgumentParser(description='FMC Analyser')
    parser.add_argument('-H', '--host', required=True, help='IP address of FMC')
    parser.add_argument('-U', '--username', required=True, help='FMC login username')
    parser.add_argument('-P', '--password', required=True, help='FMC login password')
    parser.add_argument('-A', '--acp', required=False, default='all', help='Rule name you want to analyse. Leave blank for default "all"')
    parser.add_argument('-C', '--config', required=False, default='config.yml', help='Config file path. Leave blank for default: config.yml')
    ARGS = parser.parse_args()

    fmcloader = FMCLoader(ARGS.host, ARGS.username, ARGS.password, ARGS.acp)
    print('OK')

    print('Building models ... ', end='', flush=True)
    builder = Builder(fmcloader)
    print('OK')

    try:
        print('Parsing data ... ', end='', flush=True)
        data = Data(builder, ARGS.config)
    except FileNotFoundError:
        msg = 'File {} not found.'.format(ARGS.config)
        sys.stderr.write(msg)
        sys.exit(1)
    print('OK')

    print('Exporting to Excel ... ', end='', flush=True)
    exp = Export()
    exp.export_to_excel(data.access_policies_data, exp.access_policy_header, 'access_policies_information')
    for policy in builder.policies:
        exp.export_to_excel(
            data.access_rules_data[policy.name],
            exp.access_rule_header,
            'access_rules_of_{}'.format(policy.name),
        )
    exp.export_to_excel(data.ports_data, exp.port_header, 'ports')
    exp.export_to_excel(data.networks_data, exp.network_header, 'networks')
    print('OK')

    print('Formatting Excel ... ', end='', flush=True)
    wb = openpyxl.load_workbook('./exports/final.xlsx')
    for sheet_name in wb.sheetnames:
        exp.format_column(wb[sheet_name])
        exp.format_row(wb[sheet_name])
    wb.save('./exports/final.xlsx')
    print('OK')

    print('--- The Analysis is complete! ---')
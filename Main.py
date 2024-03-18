import argparse
from FMCLoader import FMCLoader
from Logic.BuilderLogic import Builder
from Logic.DataLogic import Data
from Logic.Model import Model
import ExportToExcel as exp
  
if __name__ == "__main__":
        try:
                parser = argparse.ArgumentParser(description='FMC Analyser')
                parser.add_argument('-h', '--host', required=True, help='ip address of FMC')
                parser.add_argument('-u', '--username', required=True, help='enter username')
                parser.add_argument('-p', '--password', required=True, help='enter password')
                parser.add_argument('-a', '--acp', required=False, choices=['acp', 'ports', 'networks'], default='all', help='chose from list or leave it blank and run all by default')
                parser.add_argument('-c', '--config', required=False, default='config.ini', help='enter the configurationn file or leave it blank and run config.ini by default')

                ARGS = parser.parse_args()

                fmcloader = FMCLoader(ARGS.host, ARGS.username, ARGS.password, ARGS.acp)
        except:
                fmcloader = FMCLoader('192.168.33.193', 'admin', 'GetCon135!!', 'all')

        builder = Builder(fmcloader)
        data = Data(builder)

        for policy in builder.policies:
                exp.export_to_excel(data.access_rules_data[policy.name], exp.ACCESS_RULE_HEADER, 'access_rules_of_{}'.format(policy.name))
        exp.export_to_excel(data.ports_data, exp.PORTS_HEADER, 'ports')
        exp.export_to_excel(data.networks_data, exp.NETWORK_HEADER, 'networks')

        print('Done')
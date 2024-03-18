import pandas as pd
import os

ACCESS_RULE_HEADER = ['Access Rule', 'Action', 'Enabled', 'Source Networks', 'Source Zones', 'Source Ports', 'Destination Networks', 'Destination Zones', 'Destination Ports']
PORTS_HEADER = ['Group Name', 'Name', 'Protocol', 'Port', 'Size', 'Risky', 'Equal with']
NETWORK_HEADER = ['Group Name', 'Group depth', 'Name', 'Value', 'Size', 'Equal with']

def export_to_excel(data, header, sheet_name):
        df = pd.DataFrame(data, columns=header)
        df.index = range(1, len(df)+1)
        export_dir = os.getcwd() + '/Exports/final.xlsx'
        with pd.ExcelWriter(path=export_dir, mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(excel_writer=writer, sheet_name=sheet_name)
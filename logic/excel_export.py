import os

import pandas as pd

ACCESS_POLICY_HEADER = ['Name', 'Count Of Enabled Rules', 'Count Of Allowed Rules', 'Ratio Of Enabled Rules', 'Ratio Of Allowed Rules', 'Average Source Network Size', 'Average Destination Network Size', 'Average Destination Port Size',]
ACCESS_RULE_HEADER = ['Name', 'Action', 'Enabled', 'Source Zones', 'Source Networks', 'Source Ports', 'Destination Zones', 'Destination Networks', 'Destination Ports', 'Source Networks Size', 'Destination Networks Size', 'Destination Ports Size', 'Source Network Category', 'Relative Source Network Category', 'Destination Network Category', 'Relative Destination Network Category', 'Destination Port Category', 'Relative Destination Port Category']
PORTS_HEADER = ['Group Name', 'Name', 'Protocol', 'Port', 'Size', 'Risky', 'Duplicates', 'Reference Count from Rules']
NETWORK_HEADER = ['Group Name', 'Group depth', 'Name', 'Value', 'Size', 'Subnet', 'Duplicates', 'Reference Count from Rules']

def export_to_excel(data: list[str], header: list[str], sheet_name: str) -> None:
    df = pd.DataFrame(data, columns=header)
    df.index = range(1, len(df)+1)
    export_dir = os.getcwd() + '/exports/final.xlsx'
    if os.path.exists(export_dir):
        with pd.ExcelWriter(path=export_dir, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
            df.to_excel(excel_writer=writer, sheet_name=sheet_name)
    else:
        with pd.ExcelWriter(path=export_dir) as writer:
            df.to_excel(excel_writer=writer, sheet_name=sheet_name)

import os

import pandas as pd

ACCESS_POLICY_HEADER = ['Name', 'Count Of Enabled Rules', 'Count Of Allowed Rules', 'Ratio Of Enabled Rules', 'Ratio Of Allowed Rules']
ACCESS_RULE_HEADER = ['Access Rule', 'Action', 'Enabled', 'Source Networks', 'Source Zones', 'Source Ports', 'Destination Networks', 'Destination Zones', 'Destination Ports', 'Destination Port Category', 'Relative Destination Port Category', 'Source Network Category', 'Destination Network Category', 'Relative Source Network Category', 'Relative Destination Network Category']
PORTS_HEADER = ['Group Name', 'Name', 'Protocol', 'Port', 'Size', 'Risky', 'Equal with', 'Count of Port object in Rules']
NETWORK_HEADER = ['Group Name', 'Group depth', 'Name', 'Value', 'Size', 'Equal with', 'Count of Network object in Rules']

def export_to_excel(data: list[str], header: list[str], sheet_name: str):
    df = pd.DataFrame(data, columns=header)
    df.index = range(1, len(df)+1)
    export_dir = os.getcwd() + '/exports/final.xlsx'
    if os.path.exists(export_dir):
        with pd.ExcelWriter(path=export_dir, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
            df.to_excel(excel_writer=writer, sheet_name=sheet_name)
    else:
        with pd.ExcelWriter(path=export_dir) as writer:
            df.to_excel(excel_writer=writer, sheet_name=sheet_name)

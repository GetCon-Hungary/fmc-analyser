import os
import pandas as pd
from openpyxl.styles import Font
from openpyxl.styles import Alignment

ACCESS_POLICY_HEADER = ['Name', 'Count Of Enabled Rules', 'Count Of Allowed Rules', 'Ratio Of Enabled Rules', 'Ratio Of Allowed Rules', 'Average Source Network Size', 'Average Destination Network Size', 'Average Destination Port Size',]
ACCESS_RULE_HEADER = ['Name', 'Action', 'Enabled', 'Source Zones', 'Source Networks', 'Source Ports', 'Destination Zones', 'Destination Networks', 'Destination Ports', 'Source Networks Size', 'Destination Networks Size', 'Destination Ports Size', 'Source Network Category', 'Relative Source Network Category', 'Destination Network Category', 'Relative Destination Network Category', 'Destination Port Category', 'Relative Destination Port Category']
PORTS_HEADER = ['Group Name', 'Name', 'Protocol', 'Port', 'Size', 'Risky', 'Duplicates', 'Reference Count from Rules']
NETWORK_HEADER = ['Group Name', 'Group depth', 'Name', 'Value', 'Size', 'Subnet', 'Duplicates', 'Reference Count from Rules']

def export_to_excel(data: list[str], header: list[str], sheet_name: str) -> None:
    """Export the specified data to excel.

        Args:
        ----
            data: The specified data to export.
            header: The specified header for data
            sheet_name: The name of the sheet

    """
    df = pd.DataFrame(data, columns=header)
    df.index = range(1, len(df)+1)
    export_dir = os.getcwd() + '/exports/final.xlsx'
    if os.path.exists(export_dir):
        with pd.ExcelWriter(path=export_dir, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
            df.to_excel(excel_writer=writer, sheet_name=sheet_name)
    else:
        with pd.ExcelWriter(path=export_dir) as writer:
            df.to_excel(excel_writer=writer, sheet_name=sheet_name)

def format_rows_font_size(ws):
        for row in range(1, ws.max_row + 1):
            for col in range(1, ws.max_column + 1):
                if row > 1:
                    ws.cell(row=row, column = col).font = Font(size=14)
                    ws.cell(row=row, column = col).alignment = Alignment(wrapText=True, horizontal='center', vertical='center')
                else:
                    ws.cell(row=1, column=col).font = Font(size=16, color="1F497D", bold=True)
                    ws.cell(row=1, column=col).alignment = Alignment(wrapText=True, horizontal='center', vertical='center')

def format_row_dimension( ws):
    for row in ws.iter_rows():
        max_line = 0
        for cell in row:
            lines = str(cell.value).count('\n') + 1
            if lines > max_line:
                max_line = lines
        ws.row_dimensions[cell.row].height = 20 * max_line

def format_column_dimension(ws):
    for column in ws.iter_cols():
        max_length = 0
        for cell in column:
            if '\n' not in str(cell.value):
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
        adjusted_width = (max_length + 2) * 2
        ws.column_dimensions[cell.column_letter].width = adjusted_width
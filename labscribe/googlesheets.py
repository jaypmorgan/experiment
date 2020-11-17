# internal imports
from typing import Dict, Optional

# external imports
import gspread


def add_new_row(sheet, data):
    sheet.append_row(data)


def update_row(sheet, cell, data):
    for idx, d in enumerate(data):
        sheet.update_cell(cell.row, cell.col + idx, data[idx])


def upload_results(sheet_name: str, exp_name: str, results: Dict[str, int], worksheet_name: Optional[str] = None) -> None:
    """
    Upload the results to googlesheets. If no row with the exp_name
    exists, then a new row will be added. If the experiment does
    exist, the row will simply be updated.
    """
    gc = gspread.service_account()
    sh = gc.open(sheet_name)
    if worksheet_name is None:
        worksheet_name = sh.sheet1.title
    ws = sh.worksheet(worksheet_name)

    data = [exp_name] + [v for v in results.values()]

    try:
        cell = ws.find(exp_name)
        update_row(ws, cell, data)
    except gspread.CellNotFound:
        add_new_row(ws, data)
# internal imports
from typing import Dict

# external imports
import gspread


def add_new_row(sheet, data):
    sheet.append_row(data)


def update_row(sheet, cell, data):
    for idx, d in enumerate(data):
        sheet.update_cell(cell.row, cell.col + idx, data[idx])


def upload_results(sheet_name: str, exp_name: str, results: Dict[str, int]) -> None:
    """
    Upload the results to googlesheets. If no row with the exp_name
    exists, then a new row will be added. If the experiment does
    exist, the row will simply be updated.
    """
    gc = gspread.service_account()
    sh = gc.open(sheet_name)
    data = [exp_name] + [v for v in results.values()]

    try:
        cell = sh.sheet1.find(exp_name)
        update_row(sh.sheet1, cell, data)
    except gspread.CellNotFound:
        add_new_row(sh.sheet1, data)

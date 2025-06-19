import re

from pyxlsb import open_workbook
from tqdm import tqdm
import pandas as pd


TITLES_FOR_NORM = ['Кол-во по заявке', 'Поступило всего']
NEW_TITLE = 'Расхождение заявка-приход'


def extract_number(text):
    match = re.search(r'[\d.]+', str(text))
    if match:
        return str(match.group())
    return None


def replace_I_to_1(text):
    return text.replace('I', '1')


def xlsb_processing(input_file, result_file, list_name='Лист1'):
    results = []

    with open_workbook(input_file) as wb:
        with wb.get_sheet(list_name) as sheet:
            headers = None
            for row_index, row in tqdm(enumerate(sheet.rows())):
                row_values = [cell.v for cell in row]
                if row_index != 0:
                    row_dict = dict(zip(headers, row_values))
                    for title in TITLES_FOR_NORM:
                        value = row_dict.get(title, '')
                        str_value = str(value)
                        str_value = replace_I_to_1(str_value)
                        str_value = extract_number(str_value)
                        row_dict[title] = str_value
                    col_qty = pd.to_numeric(row_dict['Кол-во по заявке'],
                                            errors='coerce')
                    qty_total = pd.to_numeric(row_dict['Поступило всего'],
                                              errors='coerce')
                    if pd.notna(col_qty) and pd.notna(qty_total):
                        if qty_total > col_qty:
                            row_dict[NEW_TITLE] = (
                                float(col_qty) - float(qty_total))
                            results.append(row_dict)
                else:
                    headers = row_values
    df_result = pd.DataFrame(results)
    df_result.to_excel(result_file, index=False)


if __name__ == '__main__':
    xlsb_processing('input_data.xlsb', 'result.xlsx')

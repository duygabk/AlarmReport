import os

import openpyxl
from const import outputFolder

def check_file_exist(filePath):
    return True if os.path.exists(filePath) else False

def create_new_book(filePath):
    wb = openpyxl.Workbook()
    wb.save(filePath)

filePath = outputFolder + "DrawChart.xlsx"

print(
    check_file_exist(filePath)
)

create_new_book(filePath)
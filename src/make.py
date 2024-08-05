import mysql.connector
from openpyxl import Workbook
from openpyxl.styles import Font
from src.sendmail import sendmail

def save():
    database_config = {
        'host': '',
        'port': 3306,
        'user': 'nandu',
        'password': 'Nk@1412',
        'database': 'FA',
    }
    mydb = mysql.connector.connect(**database_config)
    cursor = mydb.cursor()

    sql_query = "SELECT * FROM periods"

    cursor.execute(sql_query)
    data = cursor.fetchall()

    wb = Workbook()
    ws = wb.active

    columns = [i[0] for i in cursor.description]
    ws.append(columns)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for row in data:
        ws.append(row)

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter

        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass

        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    wb.save("data.xlsx")

    sendmail()

    query1 = f"UPDATE daywise SET login = NULL,logout = NULL"
    cursor.execute(query1)
    mydb.commit()

    query2 = f"UPDATE periods SET period1 = NULL, period2 = NULL, period3 = NULL, period4 = NULL, period5 = NULL, period6 = NULL, period7 = NULL"
    cursor.execute(query2)
    mydb.commit()

    mydb.close()

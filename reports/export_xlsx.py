import xlsxwriter

def create_export_xlsx_users(users):
    
    file_name = 'user_list.xlsx'
    
    # Create an Excel file
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()

    # Write header row
    headers = ['ID', 'Username', 'First Name', 'Last Name', 'Language', 'Join Date']
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)
        
        
    # Write data to Excel file
    row = 1
    for user in users:
        worksheet.write(row, 0, user.user_id)
        worksheet.write(row, 1, user.username)
        worksheet.write(row, 2, user.first_name)
        worksheet.write(row, 3, user.last_name)
        worksheet.write(row, 4, user.language_code)
        worksheet.write(row, 5, user.join_date.strftime('%Y-%m-%d %H:%M:%S'))
        row += 1

    workbook.close()
    
    return file_name
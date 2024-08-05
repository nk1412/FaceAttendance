from datetime import datetime, timedelta,time
import mysql.connector
from src.make import save

database_config = {
    'host': '',
    'port': 3306,
    'user': 'nandu',
    'password': 'Nk@1412',
    'database': 'FA',
}

mydb = mysql.connector.connect(**database_config)
cursor = mydb.cursor()

def calculate_attendance(login_time, logout_time):
    periods = [
        {'name': 'period1', 'start': '09:00:00', 'end': '09:50:00'},
        {'name': 'period2', 'start': '09:50:00', 'end': '10:40:00'},
        {'name': 'period3', 'start': '10:40:00', 'end': '11:30:00'},
        {'name': 'period4', 'start': '11:30:00', 'end': '12:20:00'},
        {'name': 'period5', 'start': '13:00:00', 'end': '13:50:00'},
        {'name': 'period6', 'start': '13:50:00', 'end': '14:40:00'},
        {'name': 'period7', 'start': '14:40:00', 'end': '15:30:00'},
    ]

    attendance = ['A' for _ in range(len(periods))]  # Initialize with 'Absent'

    if login_time is None or logout_time is None:
        return attendance
    
    login_time_dt = datetime.strptime(login_time, '%H:%M:%S').time()
    logout_time_dt = datetime.strptime(logout_time, '%H:%M:%S').time()

    if login_time_dt <= datetime.strptime('09:15:00', '%H:%M:%S').time() and \
       logout_time_dt >= datetime.strptime('15:15:00', '%H:%M:%S').time():
        attendance = ['P' for _ in range(len(periods))]  # Full day attendance
    else:
        for i, period in enumerate(periods):
            period_start = datetime.strptime(period['start'], '%H:%M:%S').time()
            period_start_dt = datetime.combine(datetime.today(), period_start)

            if period_start_dt + timedelta(minutes=30) <= datetime.combine(datetime.today(), logout_time_dt):
                attendance[i] = 'P'
            else:
                attendance[i] = 'A'

        if login_time_dt <= datetime.strptime('09:15:00', '%H:%M:%S').time():
            attendance[0] = 'P'
        else:
            attendance[0] = 'A'

        if logout_time_dt >= datetime.strptime('15:15:00', '%H:%M:%S').time():
            attendance[-1] = 'P'
        else:
            attendance[-1] = 'A'

    return attendance

def find(mode):
    query = f"select {mode} from daywise"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

def update(user,mode,value):        
    query = f"UPDATE periods SET `period{mode}` = %s WHERE `snum` = %s"
    cursor.execute(query, (value,user))
    mydb.commit()
    
def output(count,user):
    current_date = datetime.now().strftime("%Y-%m-%d")
    if does_column_exist(current_date):
        query = f"UPDATE output SET `{current_date}` = %s WHERE `snum` = %s"
        cursor.execute(query, (count,user))
        mydb.commit()
    else:
        column_name = current_date.replace('-', '_')
        Query = f"ALTER TABLE output ADD COLUMN `{current_date}` int"
        cursor.execute(Query)
        mydb.commit()
        output(count,user)
def does_column_exist(column_name):
    query = f"SELECT * FROM information_schema.columns WHERE table_name = 'output' AND column_name = '{column_name}'"
    cursor.execute(query)
    return cursor.fetchone() is not None

def set():
    
    results_login = find("login")
    users = find("snum")
    results_logout = find("logout")
    for i in range(0, len(users)):
        login_time = results_login[i][0]
        logout_time = results_logout[i][0]
        count = 0
        attendance_result = calculate_attendance(login_time, logout_time)
        for j in range(0,len(attendance_result)):
            update(users[i][0],j+1,attendance_result[j])
            if attendance_result[j] == 'P':
                count += 1
        
        output(count,users[i][0])
        #print(attendance_result)

    save()

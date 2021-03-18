import sqlite3
connection = sqlite3.connect('C:/Users/Dan/Documents/code/casinich/casino_test.db')
connection.row_factory = sqlite3.Row
cursor = connection.cursor()
# try:

#     print("db connected")
#     sqlite_create_table_query = '''CREATE TABLE users (
#                             id INTEGER PRIMARY KEY,
#                             nickname TEXT NOT NULL,
#                             telegram_id INTEGER NOT NULL,
#                             games INTEGER NOT NULL,
#                             wins INTEGER,
#                             balance_rub TEXT NOT NULL,
#                             balance_points TEXT NOT NULL);'''
#     cursor.execute(sqlite_create_table_query)
#     print("db created")
# except sqlite3.Error as error:
#     print("smth went wrong ", error)
    
# finally:
#     if(connection):
#         connection.close()
#         print("connection closed")
    
# TODO: сделать связь, чтобы в user содержались payments этого user'a
def check_user_exists(telegram_id):
    # return user object if user exists, return 0 if not
    t_id = (telegram_id, )
    
    cursor.execute("select * from users where telegram_id=? limit 1", t_id)
    user = cursor.fetchone()
    
    if user:
        return user
    else:
        return 0
        
        
    
def create_user(nickname, telegram_id):
    sql = """
    insert into users(nickname, telegram_id, games, wins, balance_rub, balance_points, points_time)
    values (?,?,0,0,0,500,0)
    """
    sql_dannie = (nickname, telegram_id)
    # print(bette)
    try:
        cursor.execute(sql, sql_dannie)
        connection.commit()
        return 1
    except sqlite3.Error as error:
        print("smth went wrong when creating new user ", error)
        return 0
    

def add_points(telegram_id):
    user = check_user_exists(telegram_id)
    user_points = user['balance_points']
    user_points_new = str(int(user_points) + 500)
    sql = "update users set balance_points=? where telegram_id=?"
    sql_dannie = (user_points_new, telegram_id)
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
        
    connection.commit()
    
# payments statuses = [waiting, done, cancelled]
def create_payment(telegram_id):
    # return 0 if smth went wrong
    code = telegram_id
    
    if check_old_payments(telegram_id):
        print("user has payment already")
        return 0
    
    sql = "insert into payments(telegram_id, sum, code, status) values(?,0,?,'waiting')"
    sql_dannie = (telegram_id, code)
    
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
    
    connection.commit()
    
def change_user_rub_balance(telegram_id, sum):
    user = check_user_exists(telegram_id)
    user_balacne = user['balance_rub']
    user_balance_new = str(int(user_balacne) + int(sum))
    sql = "update users set balance_rub=? where telegram_id=?"
    sql_dannie = (user_balance_new, telegram_id)
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
        
    connection.commit()

def change_payment_status(telegram_id, status):
    # returns 0 if error, returns 1 if done
    if not check_old_payments(telegram_id):
        return 0

    sql = "update payments set status=? where telegram_id=?"
    sql_dannie = (status, telegram_id)
    
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
    
    connection.commit()
    return 1
        
def set_sum_payment(telegram_id, sum):
    # use this function before changing payment status
    # returns 0 if error, 1 if done
    if not check_old_payments(telegram_id):
        return 0
    sql = "update payments set sum=? where telegram_id=?"
    sql_dannie = (sum, telegram_id)
    
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
    
    connection.commit()
    return 1

def check_old_payments(telegram_id):
    # if there is waiting payment returns 1 if not returns 0
    t_id = (telegram_id, )
    cursor.execute("select * from payments where telegram_id = ? and status = 'waiting'", t_id)
    user_payment = cursor.fetchone()
    
    if user_payment:
        return user_payment['code']
    else:
        return 0


    
if __name__ == "__main__":
    change_payment_status(1647564460,"done")
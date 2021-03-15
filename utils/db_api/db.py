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
    insert into users(nickname, telegram_id, games, wins, balance_rub, balance_points)
    values (?,?,0,0,0,500)
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
    
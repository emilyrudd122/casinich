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
    
# TODO: переделать add_points в change_user_points(tg_id, sum) чтобы можно было менять поинты на любую сумму
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

def add_game(telegram_id, win=0):
    """ if game was won set win=1"""
    sql = ""
    if win == 1:
        sql = "update users set games = games + 1, wins = wins + 1 where telegram_id = ?"
    else:
        sql = "update users set games = games + 1 where telegram_id = ?"
    sql_dannie = (telegram_id, )
    
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
    """takes telegram_id and amount of money to change"""
    user = check_user_exists(telegram_id)
    user_balacne = user['balance_rub']
    user_balance_new = str(int(user_balacne) + int(sum))
    sql = "update users set balance_rub=? where telegram_id=?"
    sql_dannie = (user_balance_new, telegram_id)
    
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
    print(f"user {user['telegram_id']} balance changed on {sum}rub")    
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
    """ if there is waiting payment returns 1 if not returns 0"""
    t_id = (telegram_id, )
    cursor.execute("select * from payments where telegram_id = ? and status = 'waiting'", t_id)
    user_payment = cursor.fetchone()
    
    if user_payment:
        return user_payment['code']
    else:
        return 0

def get_koloda(game_id):
    # return 0 if no koloda
    g_id = (game_id, )
    cursor.execute("select * from koloda where game_id = ?", g_id)
    koloda = cursor.fetchone()
    
    if koloda:
        return koloda
    else:
        return 0

def create_koloda(game_id):
    # return 0 if koloda already exists
    koloda = get_koloda(game_id)
    if koloda:
        return 0
    
    sql = """
    insert into koloda(game_id,two,three,four,five,six,seven,eight,nine,ten,jack,queen,king,ace)
    values(?,4,4,4,4,4,4,4,4,4,4,4,4,4)
    """
    sql_dannie = (game_id,)
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print("koloda error")
        print(error)
    
    connection.commit()
    return 1
    
    
def create_game_rub(telegram_id_host, bet_amount):
    # return 0 if user has no balance
    # code = telegram_id
    
    # if check_old_payments(telegram_id):
    #     print("user has payment already")
    #     return 0
    user = check_user_exists(telegram_id_host)
    if float(user['balance_rub']) < float(bet_amount):
        print("balance is less than needed")
        return 0
    sql = """
    insert into games
    (telegram_id_host, bet_amount, telegram_id_player, host_sum, host_cards, player_sum, player_cards, winner)
    values(?,?,0,0,0,0,0,0)
    """
    sql_dannie = (telegram_id_host, bet_amount)
    
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
    
    connection.commit()
    host_id = (telegram_id_host, )
    cursor.execute("select*from games where telegram_id_host=? and winner=0", host_id)
    g = cursor.fetchone()
    create_koloda(g['id'])
    asd = 0-int(bet_amount)
    change_user_rub_balance(telegram_id_host, int(asd))
    print(f"game created, host id={telegram_id_host}, nick={user['nickname']}")
    
    return 1

# TODO: доделать количество игр и офсет, чтобы можно было разбить список игр на страницы
def get_new_games(games_amount=0, offset=0):
    # check if games exists
    cursor.execute("select * from games where telegram_id_player=0")
    g = cursor.fetchall()
    if not g:
        # no games found
        return 0
    
    return g
    
def get_game(id):
    # returns game obj or returns 0 if no game found
    idd = (id,)
    cursor.execute("select * from games where id=? limit 1", idd)
    game = cursor.fetchone()
    if game:
        return game
    return 0

def add_player_to_game(game_id, player_id):
    sql = "update games set telegram_id_player=? where id=?"
    sql_dannie = (player_id, game_id)
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
        return 0
        
    connection.commit()
    return 1
 
def add_card_host(game_id):
    sql = "update games set host_cards=host_cards+1 where id=?"
    sql_dannie = (game_id,)
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
        return 0
        
    connection.commit()
    return 1

def add_card_player(game_id):
    sql = "update games set player_cards=player_cards+1 where id=?"
    sql_dannie = (game_id,)
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
        return 0
        
    connection.commit()
    return 1

def add_sum_host(game_id, sum):
    sql = "update games set host_sum = host_sum + ? where id=?"
    sql_dannie = (sum, game_id)
    
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
        return 0
        
    connection.commit()
    return 1

def add_sum_player(game_id, sum):
    sql = "update games set player_sum = player_sum + ? where id=?"
    sql_dannie = (sum, game_id)
    
    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
        return 0
        
    connection.commit()
    return 1

def remove_card_from_koloda(game_id, card):
    sql = "update koloda set %s = %s - 1 where game_id = %s" % (card, card, game_id)
    # cu
    
    try:
        cursor.execute(sql)
    except sqlite3.Error as error:
        print(error)
        return 0
        
    connection.commit()
    return 1

def get_promo(promocode):
    promo = (promocode,)
    cursor.execute("select * from promo where code=? limit 1", promo)
    promocode = cursor.fetchone()
    if promocode:
        return promocode
    return 0

def make_promo_used(code):
    sql = "update promo set used = used + 1 where code = ?"
    sql_dannie = (code,)

    try:
        cursor.execute(sql, sql_dannie)
    except sqlite3.Error as error:
        print(error)
        return 0
    print(f"promo #{promocode} is used now")
    connection.commit()
    return 1    
    
    

if __name__ == "__main__":
    # change_payment_status(1647564460,"done")
    # print(create_game_rub(578827447,100))
    remove_card_from_koloda(13, "two")
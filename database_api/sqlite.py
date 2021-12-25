import sqlite3
import random


class Database:
    def __init__(self, path_to_db='santa.db'):
        self.path_to_db = path_to_db
        self.create_cash_table()
        self.create_table_games()
        self.create_gamers_table()

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)


    def execute (
        self, 
        sql: str, 
        parameters: tuple = None, 
        fetchone = False,
        fetchall = False,
        commit = False 
        ):

        if parameters is None:
            parameters = tuple()

        connection = self.connection

        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)
        
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()

        return data

    @staticmethod
    def format_args(sql, parameters:dict):
        sql += ' AND '.join([
            f'{item} = ?' for item in parameters
        ])

        return sql, tuple(parameters.values())


    def create_cash_table(self):
        sql = '''
            CREATE TABLE IF NOT EXISTS cash (
                id INTEGER,
                cash_data VARCHAR(5000),
                PRIMARY KEY (id)
            );
        '''
        self.execute(sql, commit=True)

    
    def add_cash(self, id:int, cash_data:str):
        sql = '''
            INSERT OR REPLACE INTO cash (id, cash_data)
            VALUES (?, ?)
        '''
        parameters = (id, cash_data)
        self.execute(sql, parameters=parameters, commit=True)

    
    def get_cash(self, id:int):
        sql = f'SELECT * FROM cash WHERE id={id}'
        data = self.execute(sql, fetchall=True)

        return data[0][1]


    def create_gamers_table(self):
        sql = '''
            CREATE TABLE IF NOT EXISTS gamers (
                gamer_id INTEGER,
                gamer_name VARCHAR(255) NOT NULL,
                game_id INTEGER,
                wish_list VARCHAR(1000),
                letter_to_santa VARCHAR(1000),
                e_mail VARCHAR(255),
                PRIMARY KEY (gamer_id)
            );
        '''
        self.execute(sql, commit=True)


    def add_gamer(self, gamer_id:int, gamer_name:str, game_id:int, wish_list:str, letter_to_santa:str, e_mail:str):
        sql = '''
            INSERT INTO gamers (gamer_id, gamer_name, game_id, wish_list, letter_to_santa, e_mail)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        parameters = (gamer_id, gamer_name, game_id, wish_list, letter_to_santa, e_mail)
        self.execute(sql, parameters=parameters, commit=True)


    def get_gamer(self, gamer_id:int):
        '''
        Возвращает данные игрока по id
        '''
        sql = 'SELECT * FROM gamers WHERE '
        kwargs = {
            'gamer_id':gamer_id
        }
        sql, parameters = self.format_args(sql, kwargs)
        data = self.execute(sql, parameters, fetchone=True)

        return data


    def create_table_games(self):
        sql = '''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                admin_id INTEGER,
                sub_admin_id INTEGER,
                game_name VARCHAR(255),
                gift_costs INTEGER,
                gift_send_date VARCHAR(255),
                game_link VARCHAR(255),
                reg_end_date VARCHAR(255)
            );
        '''
        self.execute(sql, commit=True)


    def add_game(self, game_name:str, admin_id:int, gift_costs:int, gift_send_date:str, reg_end_date:str, game_link='empty', sub_admin_id:int=0):
        sql = '''
            INSERT INTO games (game_name, admin_id, sub_admin_id, gift_costs, gift_send_date, reg_end_date, game_link) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        parameters = (game_name, admin_id, sub_admin_id, gift_costs, gift_send_date, reg_end_date, game_link)
        self.execute(sql, parameters=parameters, commit=True)


    def update_sub_admin(self, game_id:int, sub_admin_id:str):
            sql = f'UPDATE games SET sub_admin_id="{sub_admin_id}" WHERE id={game_id}'
            self.execute(sql, commit=True)

    
    def update_game_link(self, game_id:int, game_link:str):
        sql = f'UPDATE games SET game_link="{game_link}" WHERE id={game_id}'
        self.execute(sql, commit=True)
        

    def get_games_where_user_is_admin(self, id:int):
        sql = f'SELECT * FROM games WHERE admin_id={id}'
        data = self.execute(sql, fetchall=True)

        return data


    def get_game_id(self, admin_id:int, game_name:str):
        '''
        Возвращает id игры по admin_id и названию игры
        '''
        sql = 'SELECT * FROM games WHERE '

        kwargs = {
            'admin_id':admin_id,
            'game_name':game_name
        }

        sql, parameters = self.format_args(sql, kwargs)
        data = self.execute(sql, parameters, fetchall=True)

        return data[0][0]

    
    def get_game_id_by_gamer_id(self, gamer_id:int):
        '''
        Возвращает id игры в которой учавствует игрок
        '''
        sql = 'SELECT * FROM gamers WHERE '
        kwargs = {
            'gamer_id':gamer_id
        }
        sql, parameters = self.format_args(sql, kwargs)
        data = self.execute(sql, parameters, fetchone=True)

        return data[2]


    def get_game(self, game_id:int):
        '''
        Возвращает данные игры по id
        '''
        sql = 'SELECT * FROM games WHERE '
        kwargs = {
            'id':game_id
        }
        sql, parameters = self.format_args(sql, kwargs)
        data = self.execute(sql, parameters, fetchone=True)

        return data


    def get_all_gamers_from_game(self, game_id:int):
        '''
        Возвращает список кортежей из данных игроков, пример
        [
            (1111, 'IVAN', 2, 'want iphone 13', 'Dear santa...', 'ivan@mai.ru'), 
            (2222, 'VASIA', 2, 'want iphone 13', 'Dear santa...', 'ivan@mai.ru'), 
            (3333, 'KATE', 2, 'want iphone 13', 'Dear santa...', 'ivan@mai.ru'), 
            (4444, 'DIMA', 2, 'want iphone 13', 'Dear santa...', 'ivan@mai.ru'), 
            (5555, 'PETRA', 2, 'want iphone 13', 'Dear santa...', 'ivan@mai.ru')
        ]
        
        '''
        sql = 'SELECT * FROM gamers WHERE '

        kwargs = {
            'game_id':game_id
        }

        sql, parameters = self.format_args(sql, kwargs)
        data = self.execute(sql, parameters, fetchall=True)

        return data


    def get_random_wish_list(self, game_id):
        gamers = self.get_all_gamers_from_game(game_id)
        wish_lists = [wish[3] for wish in gamers]
        random_wish = wish_lists[random.randint(0, len(wish_lists)-1)]
        
        return random_wish


if __name__ == '__main__':
    # db = Database()
    # db.add_game('other_users', 2222, 0, '29.12', '25.12')

    # db.add_gamer(1111, 'IVAN', 2, 'want iphone 13', 'Dear santa...', 'ivan@mai.ru')
    # db.add_gamer(2222, 'VASIA', 2, 'iPad pro', 'Dear santa...', 'ivan@mai.ru')
    # db.add_gamer(3333, 'KATE', 2, 'iWatch s7', 'Dear santa...', 'ivan@mai.ru')
    # db.add_gamer(4444, 'DIMA', 2, 'macBook pro', 'Dear santa...', 'ivan@mai.ru')
    # db.add_gamer(5555, 'PETRA', 2, 'iMac', 'Dear santa...', 'ivan@mai.ru')

    # result = db.get_games_where_user_is_admin(1337)
    # result = db.get_game_id(2222, 'other_users')
    # result = db.get_game_id(admin_id=1337, game_name='devman')
    # result = db.get_all_gamers_from_game(2)
    # result = db.get_game(1)
    # result = db.get_gamer(1111)
    # result = db.get_game_id_by_gamer_id(1111)
    # db.get_random_wish_list(2)

    # db.update_game_link(1, 'some_game_link')
    # db.update_sub_admin(1, 89898989)



    # print(result)
    pass

    
    




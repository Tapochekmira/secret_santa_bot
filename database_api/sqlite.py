from os import name
import sqlite3


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


    def create_table_games(self):
        sql = '''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                admin_id INTEGER,
                game_name VARCHAR(255),
                gift_costs INTEGER,
                gift_send_date VARCHAR(255),
                reg_end_date VARCHAR(255)
            );
        '''
        self.execute(sql, commit=True)


    def add_game(self, game_name:str, admin_id:int, gift_costs:int, gift_send_date:str, reg_end_date:str):
        sql = '''
            INSERT INTO games (game_name, admin_id, gift_costs, gift_send_date, reg_end_date) 
            VALUES (?, ?, ?, ?, ?)
        '''
        parameters = (game_name, admin_id, gift_costs, gift_send_date, reg_end_date)
        self.execute(sql, parameters=parameters, commit=True)


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

    
    




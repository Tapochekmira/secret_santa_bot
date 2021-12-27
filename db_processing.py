from telegram.utils import helpers

from database_api import db


def create_cache(admin_id: int, added_values: dict):
    secret_santa_db = db
    secret_santa_db.add_cash(id=admin_id, cash_data=str(added_values))


def update_cache(admin_id: int, added_values: dict):
    secret_santa_db = db
    current_game = eval(secret_santa_db.get_cash(id=admin_id))
    current_game.update(added_values)
    secret_santa_db.add_cash(id=admin_id, cash_data=str(current_game))


def get_cache_value_by_key(admin_id: int, key: str):
    secret_santa_db = db
    current_game = eval(secret_santa_db.get_cash(id=admin_id))
    return current_game[key]


def add_game_to_db(admin_id: int):
    secret_santa_db = db
    current_game = eval(secret_santa_db.get_cash(id=admin_id))
    secret_santa_db.add_game(
        game_name=current_game['game_name'],
        admin_id=admin_id,
        gift_costs=current_game['gift_costs'],
        gift_send_date=current_game['gift_send_date'],
        reg_end_date=current_game['reg_end_date'],
        game_link='empty',
        sub_admin_id=0
    )


def add_url_to_game(admin_id: int, bot_name: str):
    secret_santa_db = db
    current_game = eval(secret_santa_db.get_cash(id=admin_id))
    game_id = secret_santa_db.get_game_id(
        current_game['admin_id'],
        current_game['game_name']
    )
    game_link = helpers.create_deep_linked_url(
        bot_name,
        f'game_id{game_id}',
        group=False)
    secret_santa_db.update_game_link(game_id, game_link)

    return game_id, game_link


def get_game_from_db(game_id: int):
    secret_santa_db = db
    current_game = secret_santa_db.get_game(game_id)
    current_game = {
        'db_game_id': current_game[0],
        'admin_id': current_game[1],
        'sub_admin_id': current_game[2],
        'game_name': current_game[3],
        'gift_costs': current_game[4],
        'gift_send_date': current_game[5],
        'game_link': current_game[6],
        'reg_end_date': current_game[7],
    }
    return current_game


def get_random_wish_list(gamer_id: int):
    secret_santa_db = db
    current_gamer = eval(secret_santa_db.get_cash(id=gamer_id))
    current_game = secret_santa_db.get_game(current_gamer['game_id'])
    try:
        return secret_santa_db.get_random_wish_list(current_game[0])
    except ValueError:
        return 'Пока никто ничего не придумал, будьте первыми.'


def add_gamer_to_db(gamer_id: int):
    secret_santa_db = db
    current_gamer = eval(secret_santa_db.get_cash(id=gamer_id))
    secret_santa_db.add_gamer(
        gamer_name=current_gamer['gamer_name'],
        gamer_id=gamer_id,
        game_id=int(current_gamer['game_id']),
        wish_list=current_gamer['wish_list'],
        interests_list=current_gamer['interests_list'],
        letter_to_santa=current_gamer['letter_to_santa'],
        e_mail=current_gamer['e_mail'],
        present_to=0,
    )


def get_gamer_from_db(game_id: int, gamer_id: int):
    secret_santa_db = db
    current_gamer = secret_santa_db.get_gamer(gamer_id, game_id)
    current_gamer = {
        'db_gamer_id': current_gamer[0],
        'gamer_id': current_gamer[1],
        'gamer_name': current_gamer[2],
        'game_id': current_gamer[3],
        'wish_list': current_gamer[4],
        'interests_list': current_gamer[5],
        'santa_letter': current_gamer[6],
        'present_to': current_gamer[7],
        'e_mail': current_gamer[8],
    }
    return current_gamer


def get_gamer_games_from_db(gamer_id: int):
    secret_santa_db = db
    games_ids = secret_santa_db.get_game_ids_by_gamer_id(
        gamer_id
    )
    gamer_games = []
    for game_id in games_ids:
        gamer_games.append(
            get_game_from_db(game_id)
        )

    return gamer_games


def get_admin_games_from_db(admin_id: int):
    secret_santa_db = db
    games = secret_santa_db.get_games_where_user_is_admin(admin_id)
    admin_games = []
    for game in games:
        game_id = game[0]
        admin_games.append(get_game_from_db(game_id))
    return admin_games


def get_all_game_gamers(game_id: int):
    secret_santa_db = db
    gamers = secret_santa_db.get_all_gamers_from_game(game_id)
    game_gamers = []
    for gamer in gamers:
        game_gamers.append(
            get_gamer_from_db(
                gamer[3],
                gamer[1]
            )
        )
    return game_gamers


def change_present_to(santa: dict, recipient: dict):
    secret_santa_db = db
    secret_santa_db.update_gamer_present_to(
        santa['db_gamer_id'],
        recipient['gamer_id']
    )


def replace_gamer_parameter(gamer_id, replaceable_parameter, param_value):
    secret_santa_db = db
    secret_santa_db.update_gamer_parameter(
        gamer_id,
        replaceable_parameter,
        param_value
    )
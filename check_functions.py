import re
import time


def check_send_date(send_date, end_registration_date):
    try:
        send_date = time.strptime(send_date, '%d.%m.%Y')
        end_registration_date = time.strptime(end_registration_date, '%d.%m.%Y')
        if send_date > end_registration_date:
            return True
        return False
    except ValueError:
        return False


def get_true_game(game_name, gamer_games):
    for game in gamer_games:
        if game_name == game['game_name']:
            return game


def is_valid_email(email):
    regex = re.compile(
        r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def is_valid_name(name):
    regex = re.compile(r"([а-яА-ЯёЁ]{2,})")
    if re.fullmatch(regex, name):
        return True
    else:
        return False

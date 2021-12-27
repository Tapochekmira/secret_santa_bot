from datetime import date, datetime
from random import randint


def get_reg_end_date(reg_date):
    return reg_date.split(' до ')[1]


def get_time_to_sort(reg_end_date):
    reg_end_date = datetime.strptime(reg_end_date, '%d.%m.%Y').date()
    game_start_date = date.today()

    difference = abs(reg_end_date - game_start_date)
    seconds_in_day = 24 * 60 * 60
    return 180  # difference.days * seconds_in_day + 60 * 60 * 18.75


def drawing_of_lots(players):
    result = {}
    buffer = []
    for i in range(len(players)):
        while len(players) != len(buffer):
            index = randint(0, len(players) - 1)
            if players[index] not in buffer:
                result[players[i]] = players[index]
                buffer.append(players[index])
                break
    return result

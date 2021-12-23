from random import randint
import re

# тесовый набор
players_1 = ['Katy', 'John', 'Bill', 'Marry']  
players_2 = ['Katy', 'John']
players_3 = ['Katy', 'John', 'Bill']

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


def is_valid_email(email):
    regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
    # return re.fullmatch(regex, email)
    if re.fullmatch(regex, email):
        return True
    else:
        return False


# тест
for i in range(10):
    print(drawing_of_lots(players_1))
    print(drawing_of_lots(players_2))
    print(drawing_of_lots(players_3))


print(is_valid_email("name.surname@gmail.com"))
print(is_valid_email("anonymous123@yahoo.co.uk"))
print(is_valid_email("anonymous123@...uk"))
print(is_valid_email("...@domain.us"))
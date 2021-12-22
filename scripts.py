from random import randint

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

# тест
for i in range(10):
    print(drawing_of_lots(players_1))
    print(drawing_of_lots(players_2))
    print(drawing_of_lots(players_3))

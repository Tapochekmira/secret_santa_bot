import logging
import os
import time
from enum import Enum
from pprint import pprint
from textwrap import dedent

from dotenv import load_dotenv
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)
from telegram.utils import helpers

import keyboards
from database_api import db


class States(Enum):
    INPUT_GAME_NAME = 1
    CHECK_RESTRICTION = 2
    CHOOSE_SEND_DATE = 3
    CHOOSE_COST_LIMIT = 4
    CHOOSE_REGISTRATION_PERIOD = 5
    END_GAME_CREATION = 6
    ADMIN_TOOL_BOARD = 7
    INPUT_GAMER_NAME = 8
    INPUT_GAMER_EMAIL = 9
    INPUT_WISH_AND_INTEREST_LIST = 10
    INPUT_LETTER_TO_SANTA = 11
    FINISH_PLAYER_INFO_ENTER = 12
    INPUT_INTERESTS_LIST = 13
    INPUT_WISH_LIST = 14
    OUTPUT_PLAYER_INFO = 15


def handle_unknown(update, context):
    update.message.reply_text(
        text='Извините, но я вас не понял :(',
    )


def start(update, context):
    update.message.reply_text(
        'Организуй тайный обмен подарками, запусти праздничное настроение!',
        reply_markup=keyboards.create_game_creation_keyboard()
    )
    return States.INPUT_GAME_NAME


def input_game_name(update, context):
    update.message.reply_text('Введите название игры')
    return States.CHECK_RESTRICTION


def check_gift_cost_restriction(update, context):
    game_cache = db
    admin_id = update.message.chat_id
    current_game = {
        'game_name': update.message.text,
        'admin_id': admin_id
    }
    game_cache.add_cash(id=admin_id, cash_data=str(current_game))

    update.message.reply_text(
        'Ограничить стоимость подарка?',
        reply_markup=keyboards.create_restriction_check_keyboard()
    )
    return States.CHOOSE_REGISTRATION_PERIOD


def choose_gift_cost_limit(update, context):
    gift_cost = update.message.text
    if gift_cost == 'до 500':
        gift_cost = 1
    elif gift_cost == 'от 500 до 1000':
        gift_cost = 2
    else:
        gift_cost = 3

    game_cache = db
    admin_id = update.message.chat_id
    current_game = eval(game_cache.get_cash(id=admin_id))
    current_game['gift_costs'] = gift_cost
    print(current_game)
    game_cache.add_cash(id=admin_id, cash_data=str(current_game))

    update.message.reply_text(
        'Выберите период регистрации участников.',
        reply_markup=keyboards.create_registration_period_keyboard()
    )
    return States.CHOOSE_SEND_DATE


def choose_registration_period(update, context):
    user_choice = update.message.text
    if user_choice == 'Да':
        update.message.reply_text(
            'Выберите ценовой диапазон',
            reply_markup=keyboards.create_cost_range_keyboard()
        )
        return States.CHOOSE_COST_LIMIT

    game_cache = db
    admin_id = update.message.chat_id
    current_game = eval(game_cache.get_cash(id=admin_id))
    current_game['gift_costs'] = 0
    print(current_game)
    game_cache.add_cash(id=admin_id, cash_data=str(current_game))

    update.message.reply_text(
        'Выберите период регистрации участников.',
        reply_markup=keyboards.create_registration_period_keyboard()
    )
    return States.CHOOSE_SEND_DATE


def choose_send_gift_date(update, context):
    game_cache = db
    admin_id = update.message.chat_id
    reg_date = update.message.text
    reg_end_date = reg_date.split(' до ')[1]
    current_game = eval(game_cache.get_cash(id=admin_id))
    current_game['reg_end_date'] = reg_end_date
    print(current_game)
    game_cache.add_cash(id=admin_id, cash_data=str(current_game))

    update.message.reply_text(
        dedent('''\
        Введите дату отправки подарка
        ДД.ММ.ГГГГ
        Значения вводятся через точку.'''))

    return States.END_GAME_CREATION


def check_send_date(send_date, end_registration_date):
    try:
        send_date = time.strptime(send_date, '%d.%m.%Y')
        end_registration_date = time.strptime(end_registration_date, '%d.%m.%Y')
        if send_date > end_registration_date:
            return True
        return False
    except ValueError:
        return False


def display_game_link(update, context):
    game_cache = db
    admin_id = update.message.chat_id
    current_game = eval(game_cache.get_cash(id=admin_id))
    reg_end_date = current_game['reg_end_date']
    send_date = update.message.text

    if not check_send_date(send_date, reg_end_date):
        update.message.reply_text(
            dedent(f'''\
                Вы ввели некорректную дату отправки подарка.
                Вы ввели: {send_date}
                Попробуйте еще раз.'''))
        return States.END_GAME_CREATION

    current_game['gift_send_date'] = send_date

    new_game = db
    new_game.add_game(
        game_name=current_game['game_name'],
        admin_id=int(admin_id),
        gift_costs=int(current_game['gift_costs']),
        gift_send_date=current_game['gift_send_date'],
        reg_end_date=current_game['reg_end_date'],
        game_link='empty',
        sub_admin_id=0
    )
    game_id = new_game.get_game_id(admin_id, current_game['game_name'])

    bot = context.bot
    game_link = helpers.create_deep_linked_url(
        bot.username,
        f'game_id{game_id}',
        group=False)
    update.message.reply_text(
        dedent(f'''\
        Отлично, Тайный Санта уже готовится к раздаче подарков!
        Вот ссылка для участия в игре:
        {game_link}'''))
    new_game.update_game_link(game_id, game_link)
    pprint(new_game.get_games_where_user_is_admin(admin_id))
    return States.ADMIN_TOOL_BOARD


def welcome_new_player(update, context):
    game_id = context.args
    game_id = game_id[0].lstrip('game_id')

    current_game = db
    current_game = current_game.get_game(game_id)

    print(current_game)

    update.message.reply_text(
        dedent(f'''\
            Замечательно, ты собираешься участвовать в игре:
            Название игры: {current_game[3]}
            Ограничение стоимости подарка: {current_game[4]}
            Период регистрации участников:{current_game[5]}
            Дата отправки подарка: {current_game[7]}
            
            Укажите информацию о себе.
            Чтобы ваш "Тайный Санта" знал что вам подарить.
            
            Начнем с имени.
            Введите свое имя.'''))

    gamer_cache = db
    gamer_id = update.message.chat_id
    current_gamer = {
        'gamer_id': gamer_id,
        'game_id': game_id,
        'wish_list': '',
        'interests_list': '',
    }
    gamer_cache.add_cash(id=gamer_id, cash_data=str(current_gamer))

    print(current_gamer)

    return States.INPUT_GAMER_NAME


def input_gamer_name(update, context):
    gamer_cache = db
    gamer_id = update.message.chat_id
    current_gamer = eval(gamer_cache.get_cash(id=gamer_id))
    current_gamer['gamer_name'] = update.message.text
    gamer_cache.add_cash(id=gamer_id, cash_data=str(current_gamer))

    print(current_gamer)

    update.message.reply_text(
        dedent(f'''\
            Приятно познакомиться!
            Введите пожалуйста ваш email:'''),
    )
    return States.INPUT_GAMER_EMAIL


def input_gamer_email(update, context):
    gamer_cache = db
    gamer_id = update.message.chat_id
    current_gamer = eval(gamer_cache.get_cash(id=gamer_id))
    current_gamer['e_mail'] = update.message.text
    gamer_cache.add_cash(id=gamer_id, cash_data=str(current_gamer))

    print(current_gamer)

    return choose_wish_or_interest_list(update, context)


def choose_wish_or_interest_list(update, context):
    gamer_cache = db
    gamer_id = update.message.chat_id
    current_gamer = eval(gamer_cache.get_cash(id=gamer_id))

    update.message.reply_text(
        dedent(f'''\
        Ваш лист пожеланий:
        {current_gamer.get('wish_list')}

        Ваш лист интересов:
        {current_gamer.get('interests_list')}

        Вы можете добавить лист пожеланий и лист интересов.
        Можно добавить что-то одно или выбрать оба.
        Нажмите на соответствующую кнопку, чтобы добавить информацию.
        Чтобы перейти к следующему шагу, нажмите кнопку "Далее"'''),
        reply_markup=keyboards.create_input_wish_and_interests_keyboard()
    )
    return States.INPUT_WISH_AND_INTEREST_LIST


def ask_input_wish_list(update, context):
    update.message.reply_text(
        dedent(f'''\
        Укажите ваши пожелания, в строку через запятую.'''))
    return States.INPUT_WISH_LIST


def input_wish_list(update, context):
    gamer_cache = db
    gamer_id = update.message.chat_id
    current_gamer = eval(gamer_cache.get_cash(id=gamer_id))
    current_gamer['wish_list'] = update.message.text
    gamer_cache.add_cash(id=gamer_id, cash_data=str(current_gamer))

    print(current_gamer)

    return choose_wish_or_interest_list(update, context)


def ask_input_interest_list(update, context):
    update.message.reply_text(
        dedent(f'''\
        Укажите ваши интересы, в строку через запятую.'''))
    return States.INPUT_INTERESTS_LIST


def input_interest_list(update, context):
    gamer_cache = db
    gamer_id = update.message.chat_id
    current_gamer = eval(gamer_cache.get_cash(id=gamer_id))
    current_gamer['interests_list'] = update.message.text
    gamer_cache.add_cash(id=gamer_id, cash_data=str(current_gamer))

    print(current_gamer)

    return choose_wish_or_interest_list(update, context)


def input_message_to_santa(update, context):
    gamer_cache = db
    gamer_id = update.message.chat_id
    current_gamer = eval(gamer_cache.get_cash(id=gamer_id))
    letter_to_santa = update.message.text
    if letter_to_santa == 'Далее':
        letter_to_santa = ''
    current_gamer['letter_to_santa'] = letter_to_santa
    gamer_cache.add_cash(id=gamer_id, cash_data=str(current_gamer))

    print(current_gamer)

    update.message.reply_text(
        dedent(f'''\
        Ваше письмо Санте:
        {current_gamer.get('letter_to_santa')}
        
        Чтобы написать/заменить письмо вашему "Тайному Санте"
        Просто введите его в поле внизу. 
        Чтобы перейти к следующему шагу, нажмите "Далее"'''),
        reply_markup=keyboards.create_input_letter_to_santa_keyboard()
    )

    return States.INPUT_LETTER_TO_SANTA


def finish_player_info_enter(update, context):
    gamer_cache = db
    gamer_id = update.message.chat_id
    current_gamer = eval(gamer_cache.get_cash(id=gamer_id))

    new_gamer = db
    new_gamer.add_gamer(
        gamer_name=current_gamer['gamer_name'],
        gamer_id=int(gamer_id),
        game_id=int(current_gamer['game_id']),
        wish_list=current_gamer['wish_list'],
        letter_to_santa=current_gamer['letter_to_santa'],
        e_mail=current_gamer['e_mail'],
    )
    print(new_gamer.get_gamer(gamer_id))

    update.message.reply_text(
        dedent(f'''\
        Превосходно, ты в игре! 
        31.12.2021 мы проведем жеребьевку 
        и ты узнаешь имя и контакты своего тайного друга.
        Ему и нужно будет подарить подарок!'''))

    return output_game_info_to_gamer(update, context)


def output_game_info_to_gamer(update, context):
    games_db = db
    gamer_id = update.message.chat_id
    game_id = games_db.get_game_id_by_gamer_id(gamer_id)
    current_game = games_db.get_game(game_id)
    current_gamer = games_db.get_gamer(gamer_id)
    print(current_game)
    print(current_gamer)

    update.message.reply_text(
        dedent(f'''\
        Замечательно, ты собираешься участвовать в игре:
        Название игры: {current_game[3]}
        Ограничение стоимости подарка: {current_game[4]}
        Период регистрации участников: до {current_game[5]}
        Дата отправки подарка: {current_game[7]}

        Информация о тебе:
        Имя: {current_gamer[1]}
        Твой лист пожеланий: {current_gamer[3]}
        Твой лист интересов: current_gamer[?]
        Твое сообщение санте: {current_gamer[4]}
        Твой e_mail: {current_gamer[5]}'''))
    return States.OUTPUT_PLAYER_INFO


def run_bot(tg_token):
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "start",
                welcome_new_player,
                Filters.regex('game_id')
            ),
            CommandHandler('start', start),
        ],
        states={
            States.INPUT_GAME_NAME: [
                MessageHandler(
                    Filters.regex('^Создать игру'),
                    input_game_name
                ),
            ],
            States.CHECK_RESTRICTION: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    check_gift_cost_restriction
                ),
            ],
            States.CHOOSE_REGISTRATION_PERIOD: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    choose_registration_period
                ),
            ],
            States.CHOOSE_COST_LIMIT: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    choose_gift_cost_limit
                ),
            ],
            States.CHOOSE_SEND_DATE: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    choose_send_gift_date
                ),
            ],
            States.END_GAME_CREATION: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    display_game_link
                ),
            ],
            States.INPUT_GAMER_NAME: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    input_gamer_name
                ),
            ],
            States.INPUT_GAMER_EMAIL: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    input_gamer_email
                ),
            ],
            States.INPUT_WISH_LIST: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    input_wish_list
                ),
            ],
            States.INPUT_INTERESTS_LIST: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    input_interest_list
                ),
            ],
            States.INPUT_WISH_AND_INTEREST_LIST: [
                MessageHandler(
                    Filters.regex('^Ввести лист пожеланий'),
                    ask_input_wish_list
                ),
                MessageHandler(
                    Filters.regex('^Ввести лист интересов'),
                    ask_input_interest_list
                ),
                MessageHandler(
                    Filters.regex('^Далее'),
                    input_message_to_santa
                ),
            ],
            States.INPUT_LETTER_TO_SANTA: [
                MessageHandler(
                    Filters.regex('^Далее'),
                    finish_player_info_enter
                ),
                MessageHandler(
                    Filters.text,
                    input_message_to_santa
                ),

            ],
            States.OUTPUT_PLAYER_INFO: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    input_interest_list
                ),
            ],
        },
        fallbacks=[
            CommandHandler(
                "start",
                welcome_new_player,
                Filters.regex('game_id')
            ),
            CommandHandler('start', start),
            MessageHandler(Filters.text & ~Filters.command, handle_unknown)
        ],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    load_dotenv()
    tg_token = os.getenv('TG_TOKEN')

    run_bot(tg_token)


if __name__ == '__main__':
    main()

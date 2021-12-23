import logging
import os
import time
from enum import Enum
from textwrap import dedent

from dotenv import load_dotenv
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)
# Enable logging
from telegram.utils import helpers

import keyboards


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
    print(update.message.text)
    update.message.reply_text(
        'Ограничить стоимость подарка?',
        reply_markup=keyboards.create_restriction_check_keyboard()
    )
    return States.CHOOSE_REGISTRATION_PERIOD


def choose_gift_cost_limit(update, context):
    user_choice = update.message.text
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

    update.message.reply_text(
        'Выберите период регистрации участников.',
        reply_markup=keyboards.create_registration_period_keyboard()
    )
    return States.CHOOSE_SEND_DATE


def choose_send_gift_date(update, context):
    registration_period = update.message.text
    print(registration_period)

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
    end_registration_date = '25.12.2021'
    send_date = update.message.text
    if not check_send_date(send_date, end_registration_date):
        update.message.reply_text(
            dedent(f'''\
                Вы ввели некорректную дату отправки подарка.
                Вы ввели: {send_date}
                Попробуйте еще раз.'''))
        return States.END_GAME_CREATION
    print(send_date)

    bot = context.bot
    url = helpers.create_deep_linked_url(bot.username, 'game_id123', group=False)
    update.message.reply_text(
        dedent(f'''\
        Отлично, Тайный Санта уже готовится к раздаче подарков!
        Вот ссылка для участия в игре:
        {url}'''))

    return States.ADMIN_TOOL_BOARD


def welcome_new_player(update, context):
    payload = context.args
    print(payload)
    update.message.reply_text(
        dedent(f'''\
            Замечательно, ты собираешься участвовать в игре:
             _подставить инфу об игре_
            
            Укажите информацию о себе.
            Чтобы ваш "Тайный Санта" знал что вам подарить.
            
            Начнем с имени.
            Введите свое имя.'''))

    return States.INPUT_GAMER_NAME


def input_gamer_name(update, context):
    gamers_name = update.message.text
    print(gamers_name)
    update.message.reply_text(
        dedent(f'''\
            Приятно познакомиться!
            Введите пожалуйста ваш email:'''),
    )
    return States.INPUT_GAMER_EMAIL


def input_gamer_email(update, context):
    gamers_email = update.message.text
    print(gamers_email)

    return choose_wish_or_interest_list(update, context)


def choose_wish_or_interest_list(update, context):
    update.message.reply_text(
        dedent(f'''\
        Ваш лист пожеланий:
        _вставить лист пожеланий_

        Ваш лист интересов:
        _вставить лист интересов_

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
    print(update.message.text)
    return choose_wish_or_interest_list(update, context)


def ask_input_interest_list(update, context):
    update.message.reply_text(
        dedent(f'''\
        Укажите ваши интересы, в строку через запятую.'''))
    return States.INPUT_INTERESTS_LIST


def input_interest_list(update, context):
    print(update.message.text)
    return choose_wish_or_interest_list(update, context)


def input_message_to_santa(update, context):
    update.message.reply_text(
        dedent(f'''\
        Ваше письмо Санте:
        _вставить письмо Санте_
        
        Чтобы написать/заменить письмо вашему "Тайному Санте"
        Просто введите его в поле внизу. 
        Чтобы перейти к следующему шагу, нажмите "Далее"'''),
        reply_markup=keyboards.create_input_letter_to_santa_keyboard()
    )

    return States.INPUT_LETTER_TO_SANTA


def finish_player_info_enter(update, context):
    update.message.reply_text(
        dedent(f'''\
        Превосходно, ты в игре! 
        31.12.2021 мы проведем жеребьевку 
        и ты узнаешь имя и контакты своего тайного друга.
        Ему и нужно будет подарить подарок!'''))

    return welcome_new_player(update, context)


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

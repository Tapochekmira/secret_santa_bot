from textwrap import dedent

import db_processing
import keyboards
import values_calculation
from check_functions import get_true_game
from states import States


def welcome_new_player(update, context):
    game_id = context.args[0].lstrip('game_id')
    current_game = db_processing.get_game_from_db(game_id)
    update.message.reply_text(
        dedent(f'''\
            Замечательно, ты собираешься участвовать в игре:
            Название игры: {current_game['game_name']}
            Ограничение стоимости подарка: {current_game['gift_costs']}
            Период регистрации участников:{current_game['reg_end_date']}
            Дата отправки подарка: {current_game['gift_send_date']}

            Укажите информацию о себе.
            Чтобы ваш "Тайный Санта" знал что вам подарить.

            Начнем с имени.
            Введите свое имя.'''))

    gamer_id = update.message.chat_id
    current_gamer = {
        'gamer_id': gamer_id,
        'game_id': game_id,
        'wish_list': '',
        'interests_list': '',
    }
    db_processing.create_cache(gamer_id, current_gamer)
    return States.INPUT_GAMER_NAME


def input_gamer_name(update, context):
    db_processing.update_cache(
        update.message.chat_id,
        {'gamer_name': update.message.text}
    )
    update.message.reply_text(
        dedent(f'''\
            Приятно познакомиться!
            Введите пожалуйста ваш email:'''),
    )
    return States.INPUT_GAMER_EMAIL


def input_gamer_email(update, context):
    db_processing.update_cache(
        update.message.chat_id,
        {'e_mail': update.message.text}
    )
    return choose_wish_or_interest_list(update, context)


def choose_wish_or_interest_list(update, context):
    gamer_id = update.message.chat_id
    wish_list = db_processing.get_cache_value_by_key(gamer_id, 'wish_list')
    interests_list = db_processing.get_cache_value_by_key(gamer_id, 'interests_list')
    update.message.reply_text(
        dedent(f'''\
        Ваш лист пожеланий:
        {wish_list}

        Ваш лист интересов:
        {interests_list}

        Вы можете добавить лист пожеланий и лист интересов.
        Можно добавить что-то одно или выбрать оба.
        Нажмите на соответствующую кнопку, чтобы добавить информацию.
        Если хотите вдохновиться чьим-то листом пожеланий,\
        нажмите кнопку "Вдохновение"
        Чтобы перейти к следующему шагу, нажмите кнопку "Далее"'''),
        reply_markup=keyboards.create_input_wish_and_interests_keyboard()
    )
    return States.INPUT_WISH_AND_INTEREST_LIST


def output_random_wish_list(update, context):
    update.message.reply_text(
        dedent(f'''\
            Пример списка желаний:
            {db_processing.get_random_wish_list(update.message.chat_id)}
            ''')
    )
    return choose_wish_or_interest_list(update, context)


def ask_input_wish_list(update, context):
    update.message.reply_text(
        dedent(f'''\
        Укажите ваши пожелания, в строку через запятую.'''))
    return States.INPUT_WISH_LIST


def input_wish_list(update, context):
    db_processing.update_cache(
        update.message.chat_id,
        {'wish_list': update.message.text}
    )
    return choose_wish_or_interest_list(update, context)


def ask_input_interest_list(update, context):
    update.message.reply_text(
        dedent(f'''\
        Укажите ваши интересы, в строку через запятую.'''))
    return States.INPUT_INTERESTS_LIST


def input_interest_list(update, context):
    db_processing.update_cache(
        update.message.chat_id,
        {'interests_list': update.message.text}
    )
    return choose_wish_or_interest_list(update, context)


def input_message_to_santa(update, context):
    letter_to_santa = update.message.text
    if letter_to_santa == 'Далее':
        letter_to_santa = ''
    db_processing.update_cache(
        update.message.chat_id,
        {'letter_to_santa': letter_to_santa}
    )

    update.message.reply_text(
        dedent(f'''\
        Ваше письмо Санте:
        {letter_to_santa}

        Чтобы написать/заменить письмо вашему "Тайному Санте"
        Просто введите его в поле внизу. 
        Чтобы перейти к следующему шагу, нажмите "Далее"'''),
        reply_markup=keyboards.create_input_letter_to_santa_keyboard()
    )

    return States.INPUT_LETTER_TO_SANTA


def finish_player_info_enter(update, context):
    gamer_id = update.message.chat_id
    db_processing.add_gamer_to_db(gamer_id)
    game_id = db_processing.get_cache_value_by_key(gamer_id, 'game_id')
    current_game = db_processing.get_game_from_db(game_id)
    reg_date = current_game['reg_end_date']
    reg_end_date = values_calculation.get_reg_end_date(reg_date)
    update.message.reply_text(
        dedent(f'''\
        Превосходно, ты в игре! 
        {reg_end_date} мы проведем жеребьевку 
        и ты узнаешь имя и контакты своего тайного друга.
        Ему и нужно будет подарить подарок!'''))

    return output_players_games(update, context)


def output_players_games(update, context):
    update.message.reply_text(
        dedent(f'''\
        Вот игры, на которые вы зарегистрированы.
        Чтобы посмотреть детальную информацию об игре,
        нажмите соответствующую кнопку с названием игры.'''),
        reply_markup=keyboards.create_all_gamer_games_keyboard(
            db_processing.get_gamer_games_from_db(update.message.chat_id)
        )
    )
    return States.ALL_PLAYERS_GAMES


def output_game_info(update, context):
    gamer_id = update.message.chat_id
    game_name = update.message.text
    gamer_games = db_processing.get_gamer_games_from_db(
        gamer_id
    )
    current_game = get_true_game(game_name, gamer_games)
    update.message.reply_text(
        dedent(f'''\
                Вы участвуете в этой игре:
                Название игры: {current_game['game_name']}
                Ограничение стоимости подарка: {current_game['gift_costs']}
                Период регистрации участников:{current_game['reg_end_date']}
                Дата отправки подарка: {current_game['gift_send_date']}
                
                Если хотите посмотреть информацию о себе в этой игре,\
                нажмите кнопку 'Про меня'.
                Чтобы вернуться ко всем играм, нажмите кнопку 'Назад'.
                '''),
        reply_markup=keyboards.create_gamer_info_keyboard()
    )
    gamer = db_processing.get_gamer_from_db(
        current_game['db_game_id'],
        gamer_id
    )
    db_gamer_id = gamer['db_gamer_id']
    db_processing.create_cache(
        gamer_id,
        {
            'db_gamer_id': db_gamer_id,
            'game_id': current_game['db_game_id'],
        })
    return States.BACK_TO_ALL_GAMES


def go_back_to_all_games(update, context):
    return output_players_games(update, context)


def output_gamer_info(update, context):
    gamer_id = update.message.chat_id
    game_id = db_processing.get_cache_value_by_key(gamer_id, 'game_id')
    gamer = db_processing.get_gamer_from_db(game_id, gamer_id)
    update.message.reply_text(
        dedent(f'''\
                name: {gamer["gamer_name"]}
                interests: {gamer["interests_list"]}
                wish: {gamer["wish_list"]}
                letter: {gamer["santa_letter"]}
                e_mail: {gamer["e_mail"]}
                
                Вы может изменить любой из параметров, \
                нажмите соответствующую кнопку
                '''
               ),
        reply_markup=keyboards.create_change_gamer_info_keyboard()
    )
    return States.CHANGE_GAMER_INFO


def input_new_gamer_info(update, context):
    update.message.reply_text(
        dedent(f'''\
           Введите новое значение'''))

    db_processing.update_cache(
        update.message.chat_id,
        {'replaceable': update.message.text}
    )
    return States.REPLACE_GAMER_INFO


def change_gamer_info(update, context):
    gamer_id = update.message.chat_id
    replaceable_parameter = db_processing.get_cache_value_by_key(
        gamer_id,
        'replaceable'
    )
    db_gamer_id = db_processing.get_cache_value_by_key(
        gamer_id,
        'db_gamer_id'
    )
    db_processing.replace_gamer_parameter(
        db_gamer_id,
        replaceable_parameter,
        update.message.text
    )
    return output_gamer_info(update, context)

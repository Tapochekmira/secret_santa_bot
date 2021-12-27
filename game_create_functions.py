from textwrap import dedent

import db_processing
import keyboards
import values_calculation
from check_functions import check_send_date
from check_functions import get_true_game
from states import States


def input_game_name(update, context):
    update.message.reply_text('Введите название игры')
    return States.CHECK_RESTRICTION


def check_gift_cost_restriction(update, context):
    admin_id = update.message.chat_id
    current_game = {
        'game_name': update.message.text,
        'admin_id': admin_id
    }
    db_processing.create_cache(admin_id, current_game)

    update.message.reply_text(
        'Ограничить стоимость подарка?',
        reply_markup=keyboards.create_restriction_check_keyboard()
    )
    return States.CHOOSE_REGISTRATION_PERIOD


def choose_gift_cost_limit(update, context):
    db_processing.update_cache(
        update.message.chat_id,
        {'gift_costs': update.message.text}
    )

    update.message.reply_text(
        'Выберите период регистрации участников.',
        reply_markup=keyboards.create_registration_period_keyboard()
    )
    return States.CHOOSE_SEND_DATE


def choose_registration_period(update, context):
    if update.message.text == 'Да':
        update.message.reply_text(
            'Выберите ценовой диапазон',
            reply_markup=keyboards.create_cost_range_keyboard()
        )
        return States.CHOOSE_COST_LIMIT

    db_processing.update_cache(
        update.message.chat_id,
        {'gift_costs': 'Нет ограничений'}
    )

    update.message.reply_text(
        'Выберите период регистрации участников.',
        reply_markup=keyboards.create_registration_period_keyboard()
    )
    return States.CHOOSE_SEND_DATE


def choose_send_gift_date(update, context):
    reg_date = update.message.text
    reg_end_date = values_calculation.get_reg_end_date(reg_date)
    time_to_sort = values_calculation.get_time_to_sort(reg_end_date)

    db_processing.update_cache(
        update.message.chat_id,
        {
            'reg_end_date': reg_date,
            'time_to_sort': time_to_sort
        }
    )

    update.message.reply_text(
        dedent('''\
        Введите дату отправки подарка
        ДД.ММ.ГГГГ
        Значения вводятся через точку.'''))

    return States.END_GAME_CREATION


def display_game_link(update, context):
    admin_id = update.message.chat_id
    reg_date = db_processing.get_cache_value_by_key(admin_id, 'reg_end_date')
    reg_end_date = values_calculation.get_reg_end_date(reg_date)
    send_date = update.message.text

    if not check_send_date(send_date, reg_end_date):
        update.message.reply_text(
            dedent(f'''\
                Вы ввели некорректную дату отправки подарка.
                Вы ввели: {send_date}
                Попробуйте еще раз.'''))
        return States.END_GAME_CREATION

    db_processing.update_cache(
        admin_id,
        {'gift_send_date': send_date}
    )

    db_processing.add_game_to_db(admin_id)
    game_id, game_link = db_processing.add_url_to_game(admin_id, context.bot.username)

    update.message.reply_text(
        dedent(f'''\
        Отлично, Тайный Санта уже готовится к раздаче подарков!
        Вот ссылка для участия в игре:
        {game_link}'''))

    context.job_queue.run_once(
        sort_after_registration_end,
        db_processing.get_cache_value_by_key(admin_id, 'time_to_sort'),
        context=game_id
    )
    return output_admin_games(update, context)


def sort_after_registration_end(context):
    all_gamers = db_processing.get_all_game_gamers(context.job.context)
    gamers_index = [i for i in range(len(all_gamers))]
    couples_santa_recipient = values_calculation.drawing_of_lots(gamers_index)
    for santa_index, recipient_index in couples_santa_recipient.items():
        db_processing.change_present_to(
            all_gamers[santa_index],
            all_gamers[recipient_index]
        )
    all_gamers = db_processing.get_all_game_gamers(context.job.context)
    for gamer_index, gamer in enumerate(all_gamers):
        recip = db_processing.get_gamer_from_db(
            gamer['game_id'],
            gamer['present_to']
        )
        present_to = (
            f'name: {recip["gamer_name"]}',
            f'telegram_id: {recip["gamer_id"]}',
            f'interests: {recip["interests_list"]}',
            f'wish: {recip["wish_list"]}',
            f'letter: {recip["santa_letter"]}',
            f'e_mail: {recip["e_mail"]}'
        )
        present_to = '\n'.join(present_to)
        context.bot.send_message(
            chat_id=gamer['gamer_id'],
            text=dedent(f'''\
            Прошла жеребьевка, вы дарите подарок \
            этому человеку:\n{present_to}
            ''')
        )


def output_admin_games(update, context):
    update.message.reply_text(
        dedent(f'''\
        Вот игры, которые вы создали.
        Чтобы посмотреть детальную информацию об игре,
        нажмите соответствующую кнопку с названием игры.'''),
        reply_markup=keyboards.create_all_gamer_games_keyboard(
            db_processing.get_admin_games_from_db(update.message.chat_id)
        )
    )
    return States.ADMIN_TOOL_BOARD


def output_game_info(update, context):
    game_name = update.message.text
    gamer_games = db_processing.get_admin_games_from_db(
        update.message.chat_id
    )
    current_game = get_true_game(game_name, gamer_games)
    update.message.reply_text(
        dedent(f'''\
                Вы создали игру:
                Название игры: {current_game['game_name']}
                Ограничение стоимости подарка: {current_game['gift_costs']}
                Период регистрации участников:{current_game['reg_end_date']}
                Дата отправки подарка: {current_game['gift_send_date']}
                Ссылка на игру: {current_game['game_link']}'''))

    all_gamers = db_processing.get_all_game_gamers(current_game['db_game_id'])
    all_gamers = [
        str((
            f'name: {gamer["gamer_name"]} ',
            f'telegram_id: {gamer["gamer_id"]} ',
            f'interests: {gamer["interests_list"]} ',
            f'wish: {gamer["wish_list"]} ',
            f'letter: {gamer["santa_letter"]} ',
            f'present_to: {gamer["present_to"]} ',
            f'e_mail: {gamer["e_mail"]} ',
        ))
        for gamer in all_gamers]
    all_gamers = '\n'.join(all_gamers)
    update.message.reply_text(
        f'''Участники игры:\n{all_gamers}'''
    )
    return output_admin_games(update, context)

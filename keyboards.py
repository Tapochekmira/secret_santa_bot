from datetime import date

from telegram import KeyboardButton, ReplyKeyboardMarkup


def make_reply_markup(keyboard):
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def create_game_creation_keyboard():
    keyboard = [
        [KeyboardButton(text='Создать игру')],
    ]
    return make_reply_markup(keyboard)


def create_restriction_check_keyboard():
    keyboard = [
        [KeyboardButton(text='Да')],
        [KeyboardButton(text='Нет')],
    ]
    return make_reply_markup(keyboard)


def create_registration_period_keyboard():
    game_start_date = date.today().strftime("%d.%m.%Y")
    keyboard = [
        [KeyboardButton(
            text=f'от {game_start_date} до 25.12.2021'
        )],
        [KeyboardButton(
            text=f'от {game_start_date} до 31.12.2021'
        )],
    ]
    return make_reply_markup(keyboard)


def create_cost_range_keyboard():
    keyboard = [
        [KeyboardButton(text='до 500')],
        [KeyboardButton(text=f'от 500 до 1000')],
        [KeyboardButton(text=f'от 1000 до 2000')],
    ]
    return make_reply_markup(keyboard)


def create_input_wish_and_interests_keyboard():
    keyboard = [
        [KeyboardButton(text='Ввести лист пожеланий')],
        [KeyboardButton(text='Ввести лист интересов')],
        [KeyboardButton(text='Далее')],
    ]
    return make_reply_markup(keyboard)


def create_input_letter_to_santa_keyboard():
    keyboard = [
        [KeyboardButton(text='Далее')],
    ]
    return make_reply_markup(keyboard)

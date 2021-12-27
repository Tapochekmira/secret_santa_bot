from telegram.ext import (Filters, MessageHandler)

import gamer_addition_functions
from states import States

gamer_states = {
    States.INPUT_GAMER_NAME: [
        MessageHandler(
            Filters.text & ~Filters.command,
            gamer_addition_functions.input_gamer_name
        ),
    ],
    States.INPUT_GAMER_EMAIL: [
        MessageHandler(
            Filters.text & ~Filters.command,
            gamer_addition_functions.input_gamer_email
        ),
    ],
    States.INPUT_WISH_LIST: [
        MessageHandler(
            Filters.text & ~Filters.command,
            gamer_addition_functions.input_wish_list
        ),
    ],
    States.INPUT_INTERESTS_LIST: [
        MessageHandler(
            Filters.text & ~Filters.command,
            gamer_addition_functions.input_interest_list
        ),
    ],
    States.INPUT_WISH_AND_INTEREST_LIST: [
        MessageHandler(
            Filters.regex('^Ввести лист пожеланий'),
            gamer_addition_functions.ask_input_wish_list
        ),
        MessageHandler(
            Filters.regex('^Ввести лист интересов'),
            gamer_addition_functions.ask_input_interest_list
        ),
        MessageHandler(
            Filters.regex('^Вдохновение'),
            gamer_addition_functions.output_random_wish_list
        ),
        MessageHandler(
            Filters.regex('^Далее'),
            gamer_addition_functions.input_message_to_santa
        ),
    ],
    States.INPUT_LETTER_TO_SANTA: [
        MessageHandler(
            Filters.regex('^Далее'),
            gamer_addition_functions.finish_player_info_enter
        ),
        MessageHandler(
            Filters.text,
            gamer_addition_functions.input_message_to_santa
        ),

    ],
    States.ALL_PLAYERS_GAMES: [
        MessageHandler(
            Filters.text & ~Filters.command,
            gamer_addition_functions.output_game_info
        ),
    ],
    States.BACK_TO_ALL_GAMES: [
        MessageHandler(
            Filters.regex('^Про меня'),
            gamer_addition_functions.output_gamer_info
        ),
        MessageHandler(
            Filters.regex('^Назад'),
            gamer_addition_functions.go_back_to_all_games
        ),
    ],
    States.CHANGE_GAMER_INFO: [
        MessageHandler(
            Filters.regex('^Назад'),
            gamer_addition_functions.go_back_to_all_games
        ),
        MessageHandler(
            Filters.text,
            gamer_addition_functions.input_new_gamer_info
        ),
    ],
    States.REPLACE_GAMER_INFO: [
        MessageHandler(
            Filters.text & ~Filters.command,
            gamer_addition_functions.change_gamer_info
        ),
    ],
}

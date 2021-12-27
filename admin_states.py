from telegram.ext import (Filters, MessageHandler)

import game_create_functions
from states import States

admin_states = {
    States.INPUT_GAME_NAME: [
        MessageHandler(
            Filters.regex('^Создать игру'),
            game_create_functions.input_game_name
        ),
    ],
    States.CHECK_RESTRICTION: [
        MessageHandler(
            Filters.text & ~Filters.command,
            game_create_functions.check_gift_cost_restriction
        ),
    ],
    States.CHOOSE_REGISTRATION_PERIOD: [
        MessageHandler(
            Filters.text & ~Filters.command,
            game_create_functions.choose_registration_period
        ),
    ],
    States.CHOOSE_COST_LIMIT: [
        MessageHandler(
            Filters.text & ~Filters.command,
            game_create_functions.choose_gift_cost_limit
        ),
    ],
    States.CHOOSE_SEND_DATE: [
        MessageHandler(
            Filters.text & ~Filters.command,
            game_create_functions.choose_send_gift_date
        ),
    ],
    States.END_GAME_CREATION: [
        MessageHandler(
            Filters.text & ~Filters.command,
            game_create_functions.display_game_link
        ),
    ],
    States.ADMIN_TOOL_BOARD: [
        MessageHandler(
            Filters.text & ~Filters.command,
            game_create_functions.output_game_info
        ),
    ],
}

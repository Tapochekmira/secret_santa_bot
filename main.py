import logging
import os

from dotenv import load_dotenv
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

import admin_states
import gamer_states
import keyboards
from gamer_addition_functions import welcome_new_player
from states import States


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
        states=admin_states.admin_states | gamer_states.gamer_states,
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

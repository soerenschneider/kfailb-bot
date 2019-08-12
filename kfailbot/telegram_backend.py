import logging
import telegram

from datetime import datetime
from datetime import timedelta

from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

_unsubscribe_prefix = "unsubscribe_from_line_"
_cmd_subscribe = "subscribe"
_cmd_unmute = "unmute"
_cmd_mute = "mute"
_silence_prefix = "silence_"


class KFailBTelegramBot:
    def __init__(self, token, db_backend):
        if not token:
            raise ValueError("No token supplied")

        if not db_backend:
            raise ValueError("No backend supplied")

        self._db = db_backend
        self.updater = Updater(token=f'{token}')
        self._bot = telegram.Bot(token=f'{token}')

        self.__add_handlers()
        self.updater.start_polling()

    def __add_handlers(self):
        """
        Adds all the handlers to the telegram bot.
        :return: None
        """
        dispatcher = self.updater.dispatcher

        menu = CallbackQueryHandler(self.unsubscribe_menu, pattern=f'^{_unsubscribe_prefix}')
        dispatcher.add_handler(menu)

        menu = CallbackQueryHandler(self.mute_menu, pattern=f'^{_silence_prefix}')
        dispatcher.add_handler(menu)

        silence_handler = CommandHandler(_cmd_mute, self.mute)
        dispatcher.add_handler(silence_handler)

        unsubscribe_handler = CommandHandler('unsubscribe', self.unsubscribe)
        dispatcher.add_handler(unsubscribe_handler)

        subscribe_handler = CommandHandler('subscribe', self.subscribe)
        dispatcher.add_handler(subscribe_handler)

        unmute_handler = CommandHandler(_cmd_unmute, self.unmute)
        dispatcher.add_handler(unmute_handler)

        info_handler = CommandHandler('info', self.cmd_info)
        dispatcher.add_handler(info_handler)

    @staticmethod
    def unsubscribe_menu_keyboard(lines):
        keyboard = [[InlineKeyboardButton(f'Line {x}', callback_data=f'{_unsubscribe_prefix}{x}') for x in lines]]
        keyboard.append([InlineKeyboardButton('All', callback_data=f'{_unsubscribe_prefix}all'),
                         InlineKeyboardButton('Cancel', callback_data=f'{_unsubscribe_prefix}cancel')])

        return InlineKeyboardMarkup(keyboard)

    def unsubscribe_menu(self, bot, update):
        """ Called when the user clicks on a button """
        query = update.callback_query
        data = query.data[len(_unsubscribe_prefix):]
        chat_id = update.effective_user.id

        text = "Cancelled"
        if 'all' == data:
            self._db.unsubscribe_from_all_lines(chat_id)
            text = "Unsubscribed from all lines"
        elif 'cancel' != data:
            self._db.unsubscribe_from_line(chat_id, int(data))
            text = f"Unsubscribed from line {data}"

        bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=text)

    def unsubscribe(self, bot, update):
        chat_id = update.message.chat_id
        lines = self._db.get_subscriptions(chat_id)
        if lines:
            markup = self.unsubscribe_menu_keyboard(lines)
            update.message.reply_text("Unsubscribe", reply_markup=markup)
        else:
            update.message.reply_text("You are not subscribed to any line, yet. \nIn order to do so, use the command"
                                      " /subscribe <line>")

    def send_message(self, text, line, is_markdown=False):
        if not text or not line:
            raise ValueError('"text" or "line" empty.')

        recipients = self._db.get_subscribers(line)
        for recipient in recipients:
            recipient = str(recipient)

            silence = self._db.read_silence(recipient)

            if not silence.is_effective():
                self._bot.send_message(chat_id=recipient, text=text)
            elif not silence.mute:
                self._bot.send_message(chat_id=recipient, text=text, disable_notification=True)

    def cmd_info(self, bot, update):
        chat_id = update.message.chat_id
        lines = self._db.get_subscriptions(chat_id)
        if lines:
            lines_str = ','.join(str(x) for x in lines)
            update.message.reply_text(f'You are subscribed to {lines_str}.')
        else:
            update.message.reply_text("You are not subscribed to any line, yet. \nIn order to do so, use the command"
                                      " /subscribe <line>")

    def mute(self, bot, update):
        chat_id = update.message.chat_id
        markup = self.mute_menu_keyboard()
        update.message.reply_text("Silence", reply_markup=markup)

    def mute_menu(self, bot, update):
        """ Called when the user clicks on a button """
        query = update.callback_query
        data = query.data[len(_cmd_mute) + 1:]
        chat_id = update.effective_user.id

        until = datetime.utcnow() + timedelta(hours=int(data))
        mute = 'completely' == data
        self._db.new_silence(chat_id, until, mute=mute)
        text = f"You will not receive any updates in the next {data} hours."

        bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=text)

    @staticmethod
    def mute_menu_keyboard():
        options = [1, 4, 8, 12, 24, 48]
        keyboard = [[InlineKeyboardButton(f'{x}h', callback_data=f'{_silence_prefix}{x}') for x in options]]
        return InlineKeyboardMarkup(keyboard)

    def subscribe(self, bot, update):
        chat_id = update.message.chat_id
        text = update.message.text
        text = text[1 + len(_cmd_subscribe):]

        try:
            line = int(text)
            self._db.subscribe_to_line(chat_id, line)

        except Exception as e:
            logging.error(f'Garbage input: {e}')
            update.message.reply_text("Could not parse line information.")
            return

        msg = f"Subscribed to line {line}"
        update.message.reply_text(msg)

    def unmute(self, bot, update):
        chat_id = update.message.chat_id

        try:
            chat_id = int(chat_id)
            self._db.delete_silence(chat_id)
            update.message.reply_text("Successfully unmuted")

        except Exception as e:
            logging.error(f'Can not unmute: {e}')
            update.message.reply_text("Could unmute, sorry.")

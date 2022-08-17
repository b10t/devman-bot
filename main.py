import datetime
import logging
import time
import traceback
from textwrap import dedent

import pytz
import requests
from environs import Env
from memory_profiler import memory_usage
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Dispatcher, Updater
from telegram.utils.helpers import escape_markdown

logger = logging.getLogger('TelegramBotLogger')

start_time = time.time()


class BotLogsHandler(logging.Handler):
    def __init__(self, telegram_bot, telegram_chat_id) -> None:
        super().__init__(logging.INFO)

        self.telegram_chat_id = telegram_chat_id
        self.telegram_bot = telegram_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.telegram_bot.send_message(
            chat_id=self.telegram_chat_id,
            text=dedent(log_entry)
        )


def get_memory_usage():
    """Возвращает кол-во используемой памяти."""
    memory = round(memory_usage().pop(), 3)
    return escape_markdown(
        f'{memory}',
        2
    )


def report(update: Update, context: CallbackContext) -> None:
    """Отчёт об текущем состоянии бота."""
    message_text = dedent(
        f'''
            *Текущий статус:*
            RAM:   `{get_memory_usage()} MiB`
            Start: `{time.ctime(start_time)}`
            UPT:   `{str(datetime.timedelta(seconds=(time.time() - start_time)))}`
        '''
    )

    # `{datetime.datetime.fromtimestamp(time.time() - start_time, pytz.utc)}`

    update.message.reply_text(
        message_text,
        parse_mode=ParseMode.MARKDOWN_V2
    )


if __name__ == '__main__':
    logging.basicConfig(format="%(message)s")
    logger.setLevel(logging.INFO)

    print(memory_usage())

    env = Env()
    env.read_env()

    telegram_token = env('TELEGRAM_TOKEN', 'TELEGRAM_TOKEN')
    telegram_chat_id = env.int('TELEGRAM_CHAT_ID', 0)
    devman_token = env('DEVMAN_TOKEN', 'DEVMAN_TOKEN')

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher
    telegram_bot = dispatcher.bot

    dispatcher.add_handler(CommandHandler('report', report))

    bot_logs_handler = BotLogsHandler(telegram_bot, telegram_chat_id)
    logger.addHandler(bot_logs_handler)

    updater.start_polling()

    user_reviews_url = 'https://dvmn.org/api/long_polling/'

    headers = {
        'Authorization': f'Token {devman_token}',
    }

    params = {}

    while True:
        try:
            try:
                response = requests.get(
                    user_reviews_url,
                    headers=headers,
                    params=params
                )
            except requests.exceptions.ReadTimeout:
                continue
            except requests.exceptions.ConnectionError:
                time.sleep(5)
                continue

            response.raise_for_status()

            reviews_result = response.json()

            if reviews_result['status'] == 'timeout':
                timestamp = reviews_result.get('timestamp_to_request')
            else:
                timestamp = reviews_result.get('last_attempt_timestamp')

                for review in reviews_result.get('new_attempts'):
                    review_status = 'Преподавателю всё понравилось, ' \
                        'можно переходить к следующему уроку.'

                    if review.get('is_negative'):
                        review_status = 'К сожалению, в работе нашлись ошибки.'

                    telegram_bot_message = f'''\
                        У Вас проверили работу "{review.get("lesson_title")}".

                        {review_status}

                        Ссылка на урок: {review.get("lesson_url")}'''

                    telegram_bot.send_message(
                        chat_id=telegram_chat_id,
                        text=dedent(telegram_bot_message)
                    )

            params.update(timestamp=timestamp)

        except Exception:
            logger.error(traceback.format_exc())

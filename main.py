import requests
import time
from environs import Env
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)


def create_and_start_bot(telegram_token):
    """Creates and launches a telegram bot."""
    updater = Updater(telegram_token)
    updater.start_polling()

    return updater.bot


if __name__ == '__main__':
    env = Env()
    env.read_env()

    telegram_token = env('TELEGRAM_TOKEN', 'TELEGRAM_TOKEN')
    telegram_chat_id = env.int('TELEGRAM_CHAT_ID', 0)
    devman_token = env('DEVMAN_TOKEN', 'DEVMAN_TOKEN')

    telegram_bot = create_and_start_bot(telegram_token)

    user_reviews_url = 'https://dvmn.org/api/long_polling/'

    headers = {
        'Authorization': f'Token {devman_token}',
    }

    params = {}

    while True:
        try:
            response = requests.get(
                user_reviews_url,
                headers=headers,
                params=params
            )
        except requests.exceptions.ReadTimeout or requests.exceptions.ConnectionError:
            time.sleep(5)
            continue

        response.raise_for_status()

        reviews_result = response.json()

        if reviews_result['status'] == 'timeout':
            timestamp = int(reviews_result.get('timestamp_to_request'))
        else:
            timestamp = int(reviews_result.get('last_attempt_timestamp')) + 1

            for review in reviews_result.get('new_attempts'):
                review_status = 'Преподавателю всё понравилось, ' \
                    'можно переходить к следующему уроку.'

                if review.get('is_negative'):
                    review_status = 'К сожалению, в работе нашлись ошибки.'

                telegram_bot_message = f'У Вас проверили работу "{review.get("lesson_title")}".\n\n' \
                    f'{review_status}\n\n' \
                    f'Ссылка на урок: {review.get("lesson_url")}'

                telegram_bot.send_message(
                    chat_id=telegram_chat_id,
                    text=telegram_bot_message
                )

        params.update(timestamp=timestamp)

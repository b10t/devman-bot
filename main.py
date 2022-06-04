import requests
from environs import Env


if __name__ == '__main__':
    env = Env()
    env.read_env()

    telegram_token = env('TELEGRAM_TOKEN', 'TELEGRAM_TOKEN')
    devman_token = env('DEVMAN_TOKEN', 'DEVMAN_TOKEN')

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
            continue

        response.raise_for_status()

        resp_json = response.json()

        print(resp_json)

        if resp_json['status'] == 'timeout':
            timestamp = int(resp_json.get('timestamp_to_request'))
        else:
            timestamp = int(resp_json.get('last_attempt_timestamp')) + 1
            # params = {}

        params.update(timestamp=timestamp)

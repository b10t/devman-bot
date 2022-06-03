import requests
from environs import Env


if __name__ == '__main__':
    env = Env()
    env.read_env()

    devman_token = env('DEVMAN_TOKEN', 'DEVMAN_TOKEN')

    user_reviews_url = 'https://dvmn.org/api/long_polling/'

    headers = {
        'Authorization': f'Token {devman_token}',
    }

    params = {}

    while True:
        response = requests.get(
            user_reviews_url,
            headers=headers,
            params=params
        )
        response.raise_for_status()

        resp_json = response.json()

        print(resp_json)

        if 'status' in resp_json and resp_json['status'] == 'timeout':
            params.update(timestamp=resp_json.get('timestamp_to_request'))

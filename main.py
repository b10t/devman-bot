import requests
from environs import Env


if __name__ == '__main__':
    env = Env()
    env.read_env()

    devman_token = env('DEVMAN_TOKEN', 'DEVMAN_TOKEN')

    user_reviews_url = 'https://dvmn.org/api/user_reviews/'

    headers = {
        'Authorization': f'Token {devman_token}',
    }

    response = requests.get(user_reviews_url, headers=headers)
    response.raise_for_status()

    print(response.text)

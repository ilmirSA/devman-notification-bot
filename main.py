import asyncio
import os
import time

import requests
import telegram
from dotenv import load_dotenv


def long_polling(token):
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': token,
    }
    while True:
        response = requests.get(url, headers=headers, timeout=91)
        response.raise_for_status()
        decode_response = response.json()

        if decode_response['status'] == 'timeout':
            params = {
                'timestamp': decode_response['timestamp_to_request']
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            decode_response = response.json()
            if decode_response['status'] == 'found':
                lesson_title = decode_response['new_attempts'][0]['lesson_title']
                is_negative = decode_response['new_attempts'][0]['is_negative']
                lesson_url = decode_response['new_attempts'][0]['lesson_url']
                return lesson_title, is_negative, lesson_url

        else:
            lesson_title = decode_response['new_attempts'][0]['lesson_title']
            is_negative = decode_response['new_attempts'][0]['is_negative']
            lesson_url = decode_response['new_attempts'][0]['lesson_url']
            return lesson_title, is_negative, lesson_url


async def bot(TG_TOKEN, TG_CHAT_ID, lesson_title, is_negative, lesson_url):
    bot = telegram.Bot(TG_TOKEN)
    if is_negative:
        async with bot:
            await bot.send_message(
                text=f'Преподаватель проверил работу!!  \"{lesson_title}\"  {lesson_url} К сожалению, в работе нашлись ошибки.',
                chat_id=TG_CHAT_ID
            )
    if not is_negative:
        async with bot:
            await bot.send_message(
                text=f'Преподаватель проверил работу!!  \"{lesson_title}\"  {lesson_url} Преподавателю все понравилосб, можно приступать к следущему уроку!',
                chat_id=TG_CHAT_ID
            )


def main():
    load_dotenv()
    devman_token = os.getenv('DEVMAN_TOKEN')
    TG_TOKEN = os.getenv('TG_TOKEN')
    TG_CHAT_ID = os.getenv('TG_CHAT_ID')

    try:
        lesson_title, is_negative, lesson_url = long_polling(devman_token)

        if lesson_title and is_negative and lesson_url:
            asyncio.run(bot(
                TG_TOKEN,
                TG_CHAT_ID,
                lesson_title,
                is_negative,
                lesson_url
            ))
            main()

    except requests.exceptions.ReadTimeout:
        main()

    except requests.exceptions.ConnectionError:
        while True:
            try:
                response = requests.get('https://dvmn.org/').status_code
                if response == 200:
                    print('Интернет есть')
                    main()
            except requests.exceptions.ConnectionError:
                print('Интернета нету')
                sleep_seconds = 1
                time.sleep(sleep_seconds)


if __name__ == '__main__':
    main()

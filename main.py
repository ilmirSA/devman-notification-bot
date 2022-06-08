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

    params = {
        'timestamp': '',
    }
    while True:
        try:
            response = requests.get(url, headers=headers, timeout=95, params=params)
            response.raise_for_status()
            checks_information = response.json()

            if checks_information['status'] == 'timeout':
                params['timestamp'] = checks_information['timestamp_to_request']

            if checks_information['status'] == 'found':
                params['timestamp'] = checks_information['new_attempts'][0]['timestamp']

                lesson_title = checks_information['new_attempts'][0]['lesson_title']
                is_negative = checks_information['new_attempts'][0]['is_negative']
                lesson_url = checks_information['new_attempts'][0]['lesson_url']

                asyncio.run(telegram_send_message(
                    lesson_title,
                    is_negative,
                    lesson_url
                ))
        except requests.exceptions.ReadTimeout:
            print('сервер не  ответил ')

        except requests.exceptions.ConnectionError:
            timeout_seconds = 5
            time.sleep(timeout_seconds)


async def telegram_send_message(lesson_title, is_negative, lesson_url):
    positive_text = f'Преподаватель проверил работу!!  \"{lesson_title}\"  {lesson_url} Преподавателю все понравилось, можно приступать к следущему уроку!'
    negative_text = f'Преподаватель проверил работу!!  \"{lesson_title}\"  {lesson_url} К сожалению, в работе нашлись ошибки.'

    async with bot:
        await bot.send_message(
            text=negative_text if is_negative else positive_text,
            chat_id=tg_chat_id
        )


if __name__ == '__main__':
    load_dotenv()
    devman_token = os.getenv('DEVMAN_TOKEN')
    tg_token = os.getenv('TG_TOKEN')
    tg_chat_id = os.getenv('TG_CHAT_ID')
    bot = telegram.Bot(tg_token)
    long_polling(devman_token)

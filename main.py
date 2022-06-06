import asyncio
import os

import requests
import telegram
from dotenv import load_dotenv


def long_polling(token):
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': token,
    }

    params = {
        "timestamp": "",
    }
    while True:
        response = requests.get(url, headers=headers, timeout=95, params=params)
        response.raise_for_status()
        information_about_checks = response.json()

        if information_about_checks['status'] == 'timeout':
            params["timestamp"] = information_about_checks['timestamp_to_request']

        if information_about_checks['status'] == 'found':
            params["timestamp"] = information_about_checks['new_attempts'][0]['timestamp']
            lesson_title = information_about_checks['new_attempts'][0]['lesson_title']
            is_negative = information_about_checks['new_attempts'][0]['is_negative']
            lesson_url = information_about_checks['new_attempts'][0]['lesson_url']
            return lesson_title, is_negative, lesson_url


async def telegram_send_message(TG_TOKEN, TG_CHAT_ID, lesson_title, is_negative, lesson_url):
    bot = telegram.Bot(TG_TOKEN)

    text = f'Преподаватель проверил работу!!  \"{lesson_title}\"  {lesson_url} К сожалению, в работе нашлись ошибки.' if is_negative else f'Преподаватель проверил работу!!  \"{lesson_title}\"  {lesson_url} Преподавателю все понравилось, можно приступать к следущему уроку!'

    async with bot:
        await bot.send_message(
            text=text,
            chat_id=TG_CHAT_ID
        )


def main():
    load_dotenv()
    devman_token = os.getenv('DEVMAN_TOKEN')
    tg_token = os.getenv('TG_TOKEN')
    tg_chat_id = os.getenv('TG_CHAT_ID')

    while True:
        try:
            lesson_title, is_negative, lesson_url = long_polling(devman_token)
            if lesson_title and is_negative and lesson_url:
                asyncio.run(telegram_send_message(
                    tg_token,
                    tg_chat_id,
                    lesson_title,
                    is_negative,
                    lesson_url
                ))


        except requests.exceptions.ReadTimeout:
            print("сервер не  ответил ")

        except requests.exceptions.ConnectionError:
            print("нету подключения к инетрнету")


if __name__ == '__main__':
    main()

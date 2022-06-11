import os
import time
import logging
import requests
import telegram
from dotenv import load_dotenv


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, tg_chat_id):
        super().__init__()
        self.tg_chat_id = tg_chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.tg_chat_id, text=log_entry)


def long_polling(token):
    logger.warning("Бот запущен")
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

                telegram_send_message(
                    lesson_title,
                    is_negative,
                    lesson_url
                )
        except Exception as err:
            logger.error("Бот Упал!")
            logger.error(err, exc_info=True)


        except requests.exceptions.ConnectionError:
            timeout_seconds = 5
            time.sleep(timeout_seconds)


def telegram_send_message(lesson_title, is_negative, lesson_url):
    positive_text = f'Преподаватель проверил работу!!  \"{lesson_title}\"  {lesson_url} Преподавателю все понравилось, можно приступать к следущему уроку!'
    negative_text = f'Преподаватель проверил работу!!  \"{lesson_title}\"  {lesson_url} К сожалению, в работе нашлись ошибки.'

    tg_bot.send_message(
        text=negative_text if is_negative else positive_text,
        chat_id=tg_chat_id
    )


if __name__ == '__main__':
    load_dotenv()
    devman_token = os.environ['DEVMAN_TOKEN']
    tg_token = os.environ['TG_TOKEN']
    tg_chat_id = os.environ['TG_CHAT_ID']
    tg_bot = telegram.Bot(tg_token)
    logger = logging.getLogger('Logger')
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(tg_bot, tg_chat_id))

    

    long_polling(devman_token)

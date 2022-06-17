import logging
import os
import time

import requests
import telegram


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, tg_chat_id):
        super().__init__()
        self.tg_chat_id = tg_chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.tg_chat_id, text=log_entry)


def long_polling(token, logger, tg_bot, tg_chat_id):
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

            response = requests.get(
                url,
                headers=headers,
                timeout=95,
                params=params
            )
            response.raise_for_status()
            checks_information = response.json()

            if checks_information['status'] == 'timeout':
                params['timestamp'] = checks_information['timestamp_to_request']

            if checks_information['status'] == 'found':
                params['timestamp'] = checks_information['last_attempt_timestamp']

                lesson_title = checks_information['new_attempts'][0]['lesson_title']
                is_negative = checks_information['new_attempts'][0]['is_negative']
                lesson_url = checks_information['new_attempts'][0]['lesson_url']

                send_telegram_message(
                    tg_bot,
                    tg_chat_id,
                    lesson_title,
                    is_negative,
                    lesson_url
                )
        except requests.exceptions.ReadTimeout:
            logger.exception("Сервер не успел овтетить!")

        except requests.exceptions.ConnectionError:
            timeout_seconds = 5
            time.sleep(timeout_seconds)

        except Exception:
            logger.exception("Бот Упал")


def send_telegram_message(tg_bot, tg_chat_id, lesson_title, is_negative, lesson_url):
    positive_text = f'Преподаватель проверил работу!!  \"{lesson_title}\"  {lesson_url} Преподавателю все понравилось, можно приступать к следущему уроку!'
    negative_text = f'Преподаватель проверил работу!!  \"{lesson_title}\"  {lesson_url} К сожалению, в работе нашлись ошибки.'

    tg_bot.send_message(
        text=negative_text if is_negative else positive_text,
        chat_id=tg_chat_id
    )


def main():
    devman_token = os.environ['DEVMAN_TOKEN']
    tg_token = os.environ['TG_TOKEN']
    tg_chat_id = os.environ['TG_CHAT_ID']
    tg_bot = telegram.Bot(tg_token)
    logger = logging.getLogger('Logger')
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(tg_bot, tg_chat_id))
    long_polling(devman_token, logger, tg_bot, tg_chat_id)


if __name__ == '__main__':
    main()

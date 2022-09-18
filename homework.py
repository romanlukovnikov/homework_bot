import logging
import os
import sys
import time
import typing
from http import HTTPStatus
from typing import Type

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (CantSentTelegramMessage, CurrentDateKeyNotFound,
                        GenericEndpointError, HomeworksKeyNotFound,
                        IncorrectHomeworkStatus, InvalidJSONResponseException,
                        YandexAPIResponseIsNot200)

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: критических замечаний нет!',
    'reviewing': 'Работа взята на проверку.',
    'rejected': 'Работа проверена: кое-что нужно поправить.'
}

last_message = {
    'YandexAPIResponseIsNot200': '',
    'Exception': '',
}

load_dotenv()

RETRY_TIME = int(os.getenv('RETRY_TIME'))
MAX_TLGR_MESSAGE_LENGTH = int(os.getenv('MAX_TLGR_MESSAGE_LENGTH'))
ENDPOINT = os.getenv('ENDPOINT')
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=(
        logging.StreamHandler(),
    ),
)

logger = logging.getLogger(__name__)


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправляет сообщение в чат телеграмм."""
    logger.info('Send message to telegram chat')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError as error:
        raise CantSentTelegramMessage(
            'Error to send message in telegram: {}'.format(error)
        )
    else:
        logger.info(f'Telegram message sent. Text: {message}')


def get_api_answer(current_timestamp: int) -> dict:
    """Запрашивает информацию о домашней работе через Яндекс API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    logger.info('Request Homework Yandex API')
    HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        response = requests.get(ENDPOINT, params=params, headers=HEADERS)
    except Exception as error:
        raise GenericEndpointError('Error in application: {}'.format(error))

    if response.status_code != HTTPStatus.OK:
        raise YandexAPIResponseIsNot200(
            'Http response from Homework Yandex API is not 200. '
            'response.status_code: {}. response.reason: {}.'.format(
                response.status_code,
                response.reason
            )
        )

    return response.json()


def check_response(response: dict) -> typing.Union[dict, None]:
    """Проверяет наличине необходимых ключей в ответе от Яндекс API."""
    if not isinstance(response, dict):
        raise TypeError('Yandex API response is not a dictionary type')

    if 'current_date' not in response:
        raise CurrentDateKeyNotFound(
            'No key "current_date" in Yandex API response'
        )

    homeworks = response.get('homeworks')
    if homeworks is None:
        raise HomeworksKeyNotFound('No key "homeworks" in Yandex API response')

    if not isinstance(homeworks, list):
        raise InvalidJSONResponseException(
            'Invalid JSON format in Yandex API response'
        )

    return homeworks


def parse_status(homework: dict) -> typing.Union[str, None]:
    """Извлекает статус проверки конкретной домашней работы."""
    homework_name = homework.get('homework_name')
    if not homework_name:
        raise KeyError(
            'No key "homework_name" in dictionary {}'.format(homework)
        )
    homework_status = homework.get('status')
    if not homework_status:
        raise KeyError('No key "status" in dictionary {}'.format(homework))
    verdict = HOMEWORK_STATUSES.get(homework_status)
    if verdict:
        return 'Статус работы "{}" изменился. {}'.format(
            homework_name, verdict
        )
    else:
        raise IncorrectHomeworkStatus(
            'Status {} unknown. Known statuses: {}'.format(
                homework_status, HOMEWORK_STATUSES
            )
        )


def check_tokens() -> bool:
    """Проверяет наличие необходимых токенов в файле .env."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def log_error(
    bot: telegram.Bot, exception_name: str, error: Type[Exception]
) -> None:
    """
    Отправляет сообщение об ошибке в журнал и телеграм.
    В телеграм при условии, что это новое сообщение.
    """
    message = 'Error in application: {}'.format(error)
    logger.error(message)
    if message != last_message[exception_name]:
        send_message(bot, message[:MAX_TLGR_MESSAGE_LENGTH])
        last_message[exception_name] = message


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical(
            'Not set some tokens in environment variables: '
            'PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID'
        )
        sys.exit(
            'Not set some tokens in environment variables: '
            'PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID'
        )

    current_timestamp = int(time.time())
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            response = get_api_answer(current_timestamp)
            logger.info('Response reseived from Homework Yandex API')
            homeworks = check_response(response)
            if homeworks:
                for homework in homeworks:
                    send_message(bot, parse_status(homework))
            else:
                logger.info('No changes in homework status detected')
            current_timestamp = response['current_date']
        except CantSentTelegramMessage as error:
            message = 'Error in application: {}'.format(error)
            logger.error(message)
        except YandexAPIResponseIsNot200 as error:
            log_error(bot, 'YandexAPIResponseIsNot200', error)
        except Exception as error:
            log_error(bot, 'Exception', error)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

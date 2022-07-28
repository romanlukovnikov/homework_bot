import logging
import os
import sys
import time
import typing

import requests
import telegram
from dotenv import load_dotenv

import config as cfg
from exceptions import (EnvironmentVariablesException, HomeworkKeyNotFound,
                        IncorrectHomeworkStatus, InvalidJSONResponseException,
                        YandexAPIResponseIsNot200)

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправляет сообщение в чат телеграмм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(cfg.INF_SUCCESS_SEND_MESSAGE.format(message))
    except Exception as error:
        logger.error(cfg.ERR_TELEGRAMM_FALL_SEND_MSG.format(error))


def send_error_message(bot: telegram.Bot, message: str) -> None:
    """Отправляет сообщение об ошибке в терминал и телеграмм."""
    logger.error(message)
    send_message(bot, message)


def get_api_answer(current_timestamp: int) -> dict:
    """Запрашивает информацию о домашней работе через Яндекс API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(cfg.ENDPOINT, params=params, headers=HEADERS)
    if response.status_code != 200:
        raise YandexAPIResponseIsNot200(
            cfg.ERR_API_RESPONSE_NOT_200.format(
                cfg.ENDPOINT, response.status_code
            )
        )
    return response.json()


def check_response(response: dict) -> typing.Union[dict, None]:
    """Проверяет наличине необходимых ключей в ответе от Яндекс API."""
    if type(response) != dict:
        raise TypeError(cfg.ERR_API_RESPONSE_TYPE)

    if 'homeworks' not in response:
        raise HomeworkKeyNotFound(cfg.ERR_HOMEWORK_KEY_NOT_FOUND)

    if type(response['homeworks']) != list:
        raise InvalidJSONResponseException(cfg.ERR_INVALID_JSON_YANDEX_API)

    return response['homeworks']


def parse_status(homework: dict) -> typing.Union[str, None]:
    """Извлекает статус проверки конкретной домашней работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = cfg.HOMEWORK_STATUSES.get(homework_status)
    if verdict:
        return cfg.INF_HOMEWORK_STATUS_CHANGED.format(homework_name, verdict)
    else:
        raise IncorrectHomeworkStatus(
            cfg.ERR_WRONG_HOMEWORK_STATUS.format(
                homework_status, cfg.HOMEWORK_STATUSES
            )
        )


def check_tokens() -> bool:
    """Проверяет наличие необходимых токенов в файле .env."""
    if all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)):
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""
    FIRST_ENDPOINT_ERROR = True

    if not check_tokens():
        logger.critical(cfg.ERR_NO_TOKENS)
        raise EnvironmentVariablesException(cfg.ERR_NO_TOKENS)

    current_timestamp = int(time.time())
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            response = get_api_answer(current_timestamp)
            logger.info(cfg.INF_GET_HOMEWORK_STATUS.format(cfg.ENDPOINT))
            homeworks = check_response(response)
            if len(homeworks) > 0:
                for homework in homeworks:
                    send_message(bot, parse_status(homework))
            else:
                logger.debug(cfg.INF_NO_CHANGES)
            current_timestamp = response['current_date']
        except YandexAPIResponseIsNot200 as error:
            message = cfg.ERR_GENERIC_MESSAGE.format(error)
            logger.error(message)
            if FIRST_ENDPOINT_ERROR:
                send_message(bot, message)
                FIRST_ENDPOINT_ERROR = False
        except Exception as error:
            message = cfg.ERR_GENERIC_MESSAGE.format(error)
            send_error_message(bot, message)
        finally:
            time.sleep(cfg.RETRY_TIME)


if __name__ == '__main__':
    main()

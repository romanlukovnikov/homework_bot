import logging
import os
import sys
import time
import typing
from http import HTTPStatus
from logging.handlers import RotatingFileHandler
from typing import Type
import hvac

import requests
import telegram
from dotenv import load_dotenv

import config as cfg
from exceptions import (CantSentTelegramMessage, CurrentDateKeyNotFound,
                        GenericEndpointError, HomeworksKeyNotFound,
                        IncorrectHomeworkStatus, InvalidJSONResponseException,
                        YandexAPIResponseIsNot200)

last_message = {
    'YandexAPIResponseIsNot200': '',
    'Exception': '',
}

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=(
        RotatingFileHandler(
            cfg.LOG_FILE_NAME, maxBytes=cfg.BYTES_PER_LOG,
            backupCount=cfg.LOG_ROTATION_COUNT
        ),
        logging.StreamHandler(),
    ),
)

logger = logging.getLogger(__name__)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправляет сообщение в чат телеграмм."""
    logger.info(cfg.INF_START_SEND_MESSAGE)
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError as error:
        raise CantSentTelegramMessage(
            cfg.ERR_TELEGRAMM_FALL_SEND_MSG.format(error)
        )
    else:
        logger.info(cfg.INF_SUCCESS_SEND_MESSAGE.format(message))


def get_api_answer(current_timestamp: int) -> dict:
    """Запрашивает информацию о домашней работе через Яндекс API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    logger.info(cfg.INF_START_API_CALL)
    try:
        response = requests.get(cfg.ENDPOINT, params=params, headers=HEADERS)
    except Exception as error:
        raise GenericEndpointError(cfg.ERR_GENERIC_MESSAGE.format(error))

    if response.status_code != HTTPStatus.OK:
        raise YandexAPIResponseIsNot200(
            cfg.ERR_API_RESPONSE_NOT_200.format(
                cfg.ENDPOINT, response.status_code,
                response.reason
            )
        )

    return response.json()


def check_response(response: dict) -> typing.Union[dict, None]:
    """Проверяет наличине необходимых ключей в ответе от Яндекс API."""
    if not isinstance(response, dict):
        raise TypeError(cfg.ERR_API_RESPONSE_TYPE)

    if 'current_date' not in response:
        raise CurrentDateKeyNotFound(cfg.ERR_CURRENT_DATE_KEY_NOT_FOUND)

    homeworks = response.get('homeworks')
    if homeworks is None:
        raise HomeworksKeyNotFound(cfg.ERR_HOMEWORKS_KEY_NOT_FOUND)

    if not isinstance(homeworks, list):
        raise InvalidJSONResponseException(cfg.ERR_INVALID_JSON_YANDEX_API)

    return homeworks


def parse_status(homework: dict) -> typing.Union[str, None]:
    """Извлекает статус проверки конкретной домашней работы."""
    homework_name = homework.get('homework_name')
    if not homework_name:
        raise KeyError(
            cfg.ERR_HOMEWORK_KEY_NOT_FOUND.format(homework)
        )
    homework_status = homework.get('status')
    if not homework_status:
        raise KeyError(cfg.ERR_STATUS_KEY_NOT_FOUND.format(homework))
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
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def log_error(
    bot: telegram.Bot, exception_name: str, error: Type[Exception]
) -> None:
    """
    Отправляет сообщение об ошибке в журнал и телеграм.
    В телеграм при условии, что это новое сообщение.
    """
    message = cfg.ERR_GENERIC_MESSAGE.format(error)
    logger.error(message)
    if message != last_message[exception_name]:
        send_message(bot, message[:cfg.MAX_TLGR_MESSAGE_LENGTH])
        last_message[exception_name] = message


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical(cfg.ERR_NO_TOKENS)
        sys.exit(cfg.ERR_NO_TOKENS)

    current_timestamp = int(time.time())
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            response = get_api_answer(current_timestamp)
            logger.info(cfg.INF_GET_HOMEWORK_STATUS.format(cfg.ENDPOINT))
            homeworks = check_response(response)
            if homeworks:
                for homework in homeworks:
                    send_message(bot, parse_status(homework))
            else:
                logger.info(cfg.INF_NO_CHANGES)
            current_timestamp = response['current_date']
        except CantSentTelegramMessage as error:
            message = cfg.ERR_GENERIC_MESSAGE.format(error)
            logger.error(message)
        except YandexAPIResponseIsNot200 as error:
            log_error(bot, 'YandexAPIResponseIsNot200', error)
        except Exception as error:
            log_error(bot, 'Exception', error)
        finally:
            time.sleep(cfg.RETRY_TIME)


if __name__ == '__main__':
    main()

import logging
import os
import sys
import time
from xmlrpc.client import Boolean

import requests
import telegram
from dotenv import load_dotenv
from requests import exceptions

from exceptions import EnvironmentVariablesException

load_dotenv()

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

FIRST_ENDPOINT_ERROR = True

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def send_message(bot: telegram.Bot, message: str) -> None:
    '''Отправляет сообщение в чат телеграмм'''
    try: 
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение успешно отравлено ботом. Текст сообщения: "{message}"')
    except Exception as error:
        logger.error(f'При отправке сообщения ботом возникла ошибка {error}')

    
def log_and_send_error_message(message: str) -> None:
    '''Отправляет сообщение об ошибке в терминал и телеграмм'''
    logger.error(message)
    if 'Ендпоинт' in message and not FIRST_ENDPOINT_ERROR:
        pass
    else:
        send_message(bot, message)


def get_api_answer(current_timestamp: int) -> dict:
    '''Запрашивает информацию о домашней работе через Яндекс API'''
    timestamp = current_timestamp or int(time.time())
#    params = {'from_date': timestamp}
    params = {'from_date': 1549962000}
    try:
        response = requests.get(ENDPOINT, params=params, headers=HEADERS)
        logger.info(f'Статус домашней работы успешно запрошен у ендпоинта: {ENDPOINT}')
        logger.debug(f'Параметры запроса - params = {params}, ответ сервера: {response.json()}')
        return response.json()
    except requests.ConnectionError as error:
        log_and_send_error_message(f'Ошибка подключения. Ендпоинт: {ENDPOINT}. Текст ошибки: {error}')
    except requests.Timeout as error:
        log_and_send_error_message(f'Ошибка таймаута. Ендпоинт: {ENDPOINT}. Текст ошибки: {error}')
    except requests.RequestException as error:
        log_and_send_error_message(f'Ошибка запроса. Ендпоинт: {ENDPOINT}. Текст ошибки: {error}')
    except Exception as error:
        log_and_send_error_message(f'Ошибка: {error}.')
    except:
        FIRST_ENDPOINT_ERROR = False



def check_response(response: dict) -> dict:
    '''Проверяет наличине необходимых ключей в ответе от Яндекс API'''
    if ('current_date' in response) and ('homeworks' in response):
        return response['homeworks']
    else:
        log_and_send_error_message(f'Нет ожидаемых ключей ("current_date" и/или "homeworks") в ответе сервера. Ответ: {response}')



def parse_status(homework: dict) -> str:
    '''Извлекает статус проверки конкретной домашней работы'''
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES.get('homework_status')
    if verdict is None:
        log_and_send_error_message(f'Статус {homework_status} не входит в список ожидаемых: {HOMEWORK_STATUSES}')
    else:
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> Boolean:
    '''Проверяет наличие необходимых токенов в файле ,env'''
    if all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)):
        return True
    else:
        message = ''
        if PRACTICUM_TOKEN is None:
            message += 'Не указан токен для практикума. '
        if TELEGRAM_TOKEN is None:
            message += 'Не указан токен для телеграмма. '
        if TELEGRAM_CHAT_ID is None:
            message += 'Не указан chat_id для телеграмма. '
        message += 'Проверьте корректность заполнения файла .env'
        logger.error(message)
        return False
#        raise EnvironmentVariablesException(message)


def main():
    """Основная логика работы бота."""

    check_tokens()
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks and len(homeworks) > 0:
                for homework in homeworks:
                    send_message(bot, parse_status(homework))
            elif len(homeworks) > 0:
                logger.debug(f'Со времени последней проверки изменений в статусах домашних заданий не было.')
            current_timestamp = response['current_date']
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            log_and_send_error_message(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
 



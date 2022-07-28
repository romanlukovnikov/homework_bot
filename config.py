INF_SUCCESS_SEND_MESSAGE = (
    'Сообщение успешно отравлено ботом. Текст сообщения: "{}"'
)
INF_GET_HOMEWORK_STATUS = (
    'Статус домашней работы успешно запрошен у ендпоинта: {}'
)
INF_HOMEWORK_STATUS_CHANGED = 'Изменился статус проверки работы "{}". {}'
INF_NO_CHANGES = (
    'Со времени последней проверки изменений '
    'в статусах домашних заданий не было.'
)
ERR_API_RESPONSE_NOT_200 = (
    'статус-код подключения к ендпоинту {} не равен 200. Значение: {}'
)
ERR_INVALID_JSON_YANDEX_API = (
    'Неверный формат JSON ответа API сервера Яндекса'
)
ERR_NO_TOKENS = (
    'В файле .env отсутствует один или несколько обязательных токенов: '
    'PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID'
)
ERR_TELEGRAMM_FALL_SEND_MSG = (
    "Не удалось отправить сообщение в телеграм. Ошибка: {}"
)
ERR_WRONG_HOMEWORK_STATUS = 'Статус {} не входит в список ожидаемых: {}'
ERR_GENERIC_MESSAGE = 'Сбой в работе программы: {}'
ERR_HOMEWORK_KEY_NOT_FOUND = 'В ответе Яндекс API не найден ключ "homeworks"'
ERR_API_RESPONSE_TYPE = 'Ответ от Яндекс API не является словарём'

RETRY_TIME = 600

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

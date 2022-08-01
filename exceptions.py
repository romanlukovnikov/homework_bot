class CantSentTelegramMessage(Exception):
    pass


class InvalidJSONResponseException(Exception):
    pass


class YandexAPIResponseIsNot200(Exception):
    pass


class IncorrectHomeworkStatus(Exception):
    pass


class HomeworksKeyNotFound(Exception):
    pass


class CurrentDateKeyNotFound(Exception):
    pass


class HomeworkNameKeyNotFound(Exception):
    pass


class StatusKeyNotFound(Exception):
    pass


class GenericEndpointError(Exception):
    pass

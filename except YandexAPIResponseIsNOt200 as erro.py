        except YandexAPIResponseIsNot200 as error:
            send_error_message(bot, error)
        except InvalidJSONResponseException as error:
            send_error_message(bot, f'Неверный формат JSON ответа API сервера Яндекса. Текст ошибки: {error}')
        except requests.ConnectionError as error:
            send_error_message(bot, f'Ошибка подключения. Ендпоинт: {ENDPOINT}. Текст ошибки: {error}')
        except requests.Timeout as error:
            send_error_message(bot, f'Ошибка таймаута. Ендпоинт: {ENDPOINT}. Текст ошибки: {error}')
        except requests.RequestException as error:
            send_error_message(bot, f'Ошибка запроса. Ендпоинт: {ENDPOINT}. Текст ошибки: {error}')

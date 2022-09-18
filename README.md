# Yandex homework bot
----

**Примечание**: Программа написана в рамках прохождения курса Python на Яндекс практикуме.

----

**Yandex homework bot** это telegram-бот для отправки изменений о статусе проверки домашней работы студента Яндекс Практикума

Ключевые возможности:

* **Опрос API сервиса Яндекс Практикума.** Периодический (по умолчанию раз в 10 минут) опрос API Яндекс Практикума и анализ ответа на предмет изменения статуса проверки домашнего задания студента. Каждый запрос проверяет изменения с момента предыдушего обращения к API Яндекс Практикума.

* **Отправка уведомлений в Telegram.** В случае определения изменений в статусе проверки домашнего задания студента telegram-бот отправляет сообщение получателю в telegram.

* **Журналирование работы и ошибок.** Все основные шаги работы программы журналируются в `STDOUT`. Информация о ключевых ошибках отправляется получателю в telegram.

Предварительные условия
-------------------------------

Для запуска чат-бота необходимо:
* **Наличие среды для запуска чат-бота** - в данной инструкции приведены сведения для запуска программы на `Ubuntu 20.04.3 LTS`. Возможен запуск и на Windows системах или на хостингах, представляющие сервис запуска Python программ. Предпочтительным вариантов является среда, в которой чат-бот сможет функционировать 24*7. Время последнего обращения к API Яндекс Практикума не запоминается в постоянной памяти, поэтому изменения в состоянии проверки домашней работы, которые произошли во время остановки чат-бота обнаружены не будут.

* **Создать эккаунт Telegram-бота** - для этого используется служебный бот `@BotFather`. Официальная документация [Telegram bots ](https://core.telegram.org/bots).
* **Получить telegram токен для работы с Bot API** - токен отправляется при создании вашего бота. Пример токена: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`. 
* **Получить ID своего Telegram-аккаунта** - для этого используется служебный бот `@userinfobot`, которому нужно отправить `@username`, где `username` - имя пользователя Telegram. Пример chat_id: `1073236156`
* **Получить токен от API сервиса Яндекс Практикума** - это индивидуальный токен, который связывает API запросы к сервису Яндекс Практикума именно с вашим эккаунтом. Для его получения необходимо пройти по [ссылке](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a) и авторизоваться учетными данными, используемыми для доступа к материалам курса Яндекс Практикума. Пример токена: `x3_BgBBBBBgCMRTAAYckQCCCFKFf9hvhUTWgAa4RWhgfdDXNBZXJnp45bW`
* **Создать файл `.env` в домашней папке пользователя.** Файл рекомендуется защитить разрешениями. Например: `sudo chmod 600 .env`. Процедура получения значений части переменных описана в разделе **Предварительные условия**. Список и описание переменных:
    - TELEGRAM_TOKEN - токен для отправки сообщения чат-ботом через API.
    - PRACTICUM_TOKEN - токен для запрсоса состояния домашней работы в API сервиса Яндекс Практикума.
    - TELEGRAM_CHAT_ID - ID Telegram-эккаунта на который будут отправляться сообщения о смене статуса проверки домашней работы Яндекс Практикума.
    - ENDPOINT - URL для запроса информации о домашнем задании Яндекс Практикума. Значение: `https://practicum.yandex.ru/api/user_api/homework_statuses/`
    - RETRY_TIME - интервал в секундах, через которое выполняются запросы к API Яндекс Практикума. Рекомендуемое значение: `600`
    - MAX_TLGR_MESSAGE_LENGTH - максимальное количество символов, отправляемое получателю в telegram. Все символы, свыше данного количества будут отброшены. Используется при отправке сообщений об ошибке подключения к API Яндекс Практикума. Порог может быть достигнут, если сообщение об ошибке будет расширено (для этого нужно править код). Рекомендуемое значение: `1024`

Пример файла `.env`

----

**Примечание**: Токены и chat_id в примере указаны вымышленные. С данными переменными чат-бот работать не будет

----

```sh
TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
PRACTICUM_TOKEN=x3_BgBBBBBgCMRTAAYckQCCCFKFf9hvhUTWgAa4RWhgfdDXNBZXJnp45bW
TELEGRAM_CHAT_ID=1073236156
ENDPOINT=https://practicum.yandex.ru/api/user_api/homework_statuses/
RETRY_TIME=600
MAX_TLGR_MESSAGE_LENGTH=1024
```


Запуск чат-бота в docker контейнере
--------------------

* **Установить Docker Engine** - инструкция по установке с [официального сайта](https://docs.docker.com/engine/install/). 
* **Скачать образ чат-бота в локальное Docker хранилище**
```sh
docker pull rlukovnikov/ya-hw-bot
```
* **Назначить дополнительных тэг для Docker образа (необязательный шаг)**
```sh
docker tag rlukovnikov/ya-hw-bot yabot
```
* **Создать и запустить контейнер**
```sh
docker run --name yabot --env-file .env --restart always --detach yabot
```
* **Изучить журналы запуска контейнера**
```sh
docker logs yabot
```
Если все параметры настроены правильно, должны появиться следующие строчки в журнале (время будет актуальным):
```sh
2022-09-18 06:25:53,507 - INFO - Request Homework Yandex API
2022-09-18 06:25:54,097 - INFO - Response reseived from Homework Yandex API
2022-09-18 06:25:54,097 - INFO - No changes in homework status detected
```
Запуск чат-бота в командной оболочке Linux (подходит для разработки и тестирования)
--------------------

* **Склонировать репозиторий чат-бота на локальный сервер.** 
```sh
git clone https://github.com/romanlukovnikov/homework_bot.git
```
* **Скопировать файл .env в папку проекта**
```sh
cp .env homework_bot/
```
* **Установить Package Installer for Python**
```sh
sudo apt install python3-pip
```
* **Установить виртуальное окружение для выполнения Python программ**
```sh
cd homework_bot/
python3 -m venv venv
```
* **Активировать виртуальное окружение**
```sh
source venv/bin/activate
```
* **Установить зависимости проекта в виртуальное окружение**
```sh
pip3 install -r requirements.txt
```
* **Запустить программу**
```sh
python3 homework.py
```
Если все параметры настроены правильно, в консоли должны появиться следующие строчки (время будет актуальным):
```sh
2022-09-18 06:25:53,507 - INFO - Request Homework Yandex API
2022-09-18 06:25:54,097 - INFO - Response reseived from Homework Yandex API
2022-09-18 06:25:54,097 - INFO - No changes in homework status detected
```
----

**Примечание**: Можно выполнить дополнительную проверку, чтобы убедиться, что программа будет присылать сообщения при изменении статуса домашней работы. Для этого в коде программы `homework_bot.py` надо заккоментировать строчку  `current_timestamp = int(time.time())` поставив перед ней символ `#` и после неё добавить строчку `current_timestamp = 1549962000`. Это заставит программу проверить статус домашних заданий с даты `12.02.2019, 12:00:00`. После запуска программы в консоли должны появиться строчки типа `2022-09-18 18:20:48,277 - INFO - Telegram message sent. Text: Статус работы "romanlukovnikov__hw02_community.zip" изменился. Работа проверена: критических замечаний нет!`, и текст сообщения должен быть продублирован в telegram.
*Не забудьте после проверки откатить изменения в `homework_bot.py`.

----

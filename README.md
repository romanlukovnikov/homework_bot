# Yandex homework bot
----

**Примечание**: Программа написана в рамках прохождения курса Python на Яндекс практикуме.

----

**Yandex homework bot** это telegram-бот для отправки изменений о статусе проверки домашней работы студента Яндекс Практикума

Ключевые возможности:

* **Опрос API сервиса Яндекс Практикума**: Периодический (по умолчанию раз в 10 минут) опрос API Яндекс Практикума и анализ ответа на предмет изменения статуса проверки домашнего задания студента. Каждый запрос проверяет изменения с момента предыдушего обращения к API Яндекс Практикума.

* **Отправка уведомлений в Telegram**: В случае определения изменений в статусе проверки домашнего задания студента telegram-бот отправляет сообщение получателю в telegram.

* **Журналирование работы и ошибок**: Все основные шаги работы программы журналируются в STDOUT. Информация о ключевых ошибках отправляется получателю в telegram.

Предварительные условия
-------------------------------

Для запуска чат-бота необходимо:
* **Создать эккаунт Telegram-бота** - для этого используется служебный бот @BotFather. Официальная документация [Telegram bots ](https://core.telegram.org/bots).
* **Получить токен для работы с Bot API** - токен отправляется при создании вашего бота. Пример токена: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`
* **Получить ID своего Telegram-аккаунта** - для этого используется служебный бот `@userinfobot`, которому нужно отправить `@username`, где `username` - имя пользователя Telegram. Пример chat_id: `1073236156`
* **Получить токен от API сервиса Яндекс Практикума** - это индивидуальный токен, который связывает API запросы к сервису Яндекс Практикума именно с вашим эккаунтом. Для его получения необходимо пройти по [ссылке](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a) и авторизоваться учетными данными, используемыми для доступа к материалам курса Яндекс Практикума. Пример токена: `x3_BgBBBBBgCMRTAAYckQCCCFKFf9hvhUTWgAa4RWhgfdDXNBZXJnp45bW`

Developing Vault
--------------------

If you wish to work on Vault itself or any of its built-in systems, you'll
first need [Go](https://www.golang.org) installed on your machine. Go version
1.19.1+ is *required*.

For local dev first make sure Go is properly installed, including setting up a
[GOPATH](https://golang.org/doc/code.html#GOPATH). Ensure that `$GOPATH/bin` is in
your path as some distributions bundle the old version of build tools. Next, clone this
repository. Vault uses [Go Modules](https://github.com/golang/go/wiki/Modules),
so it is recommended that you clone the repository ***outside*** of the GOPATH.
You can then download any required build tools by bootstrapping your environment:

```sh
$ make bootstrap
...
```

To compile a development version of Vault, run `make` or `make dev`. This will
put the Vault binary in the `bin` and `$GOPATH/bin` folders:

```sh
$ make dev
...
$ bin/vault
...
```

To compile a development version of Vault with the UI, run `make static-dist dev-ui`. This will
put the Vault binary in the `bin` and `$GOPATH/bin` folders:

```sh
$ make static-dist dev-ui
...
$ bin/vault
...
```

To run tests, type `make test`. Note: this requires Docker to be installed. If
this exits with exit status 0, then everything is working!

```sh
$ make test
...
```

If you're developing a specific package, you can run tests for just that
package by specifying the `TEST` variable. For example below, only
`vault` package tests will be run.

```sh
$ make test TEST=./vault
...
```

### Acceptance Tests

Vault has comprehensive [acceptance tests](https://en.wikipedia.org/wiki/Acceptance_testing)
covering most of the features of the secret and auth methods.

If you're working on a feature of a secret or auth method and want to
verify it is functioning (and also hasn't broken anything else), we recommend
running the acceptance tests.

**Warning:** The acceptance tests create/destroy/modify *real resources*, which
may incur real costs in some cases. In the presence of a bug, it is technically
possible that broken backends could leave dangling data behind. Therefore,
please run the acceptance tests at your own risk. At the very least,
we recommend running them in their own private account for whatever backend
you're testing.

To run the acceptance tests, invoke `make testacc`:

```sh
$ make testacc TEST=./builtin/logical/consul
...
```

The `TEST` variable is required, and you should specify the folder where the
backend is. The `TESTARGS` variable is recommended to filter down to a specific
resource to test, since testing all of them at once can sometimes take a very
long time.

Acceptance tests typically require other environment variables to be set for
things such as access keys. The test itself should error early and tell
you what to set, so it is not documented here.

For more information on Vault Enterprise features, visit the [Vault Enterprise site](https://www.hashicorp.com/products/vault/?utm_source=github&utm_medium=referral&utm_campaign=github-vault-enterprise).
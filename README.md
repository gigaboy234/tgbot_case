# HR Onboarding Bot (aiogram)

Telegram-бот для пошагового онбординга нового сотрудника на `aiogram 3`.

## Что внутри

- сценарный онбординг с контактами и кнопками
- сохранение пользователей, состояний, обращений и ошибок в SQLite
- модульная структура проекта
- заглушки для PDF, изображений и ссылок
- опциональная отправка обращений в служебный чат

## Структура проекта

```text
hr_onboarding_bot_aiogram/
├── main.py
├── config.py
├── texts.py
├── db.py
├── states.py
├── requirements.txt
├── .env.example
├── README.md
├── files/
│   ├── images/
│   │   └── director.jpg
│   ├── pdf/
│   │   └── about_company.pdf
│   └── presentations/
│       ├── block_1_safety.pdf
│       ├── block_2_communications.pdf
│       ├── block_3_hr.pdf
│       ├── block_4_useful_info.pdf
│       ├── block_5_union.pdf
│       └── block_6_services.pdf
└── handlers/
    ├── __init__.py
    ├── common.py
    ├── keyboards.py
    ├── menu.py
    └── onboarding.py
```

## Подробный запуск на Mac

### 1. Установи Python

Проверь, есть ли Python 3.11+:

```bash
python3 --version
```

Если Python нет или версия слишком старая, удобнее поставить через Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
```

Снова проверь версию:

```bash
python3 --version
```

### 2. Распакуй архив и открой папку

Например, если архив лежит в `Downloads`:

```bash
cd ~/Downloads
unzip hr_onboarding_bot_aiogram.zip
cd hr_onboarding_bot_aiogram
```

### 3. Создай виртуальное окружение

```bash
python3 -m venv venv
```

### 4. Активируй окружение

```bash
source venv/bin/activate
```

После этого в начале строки терминала появится `(venv)`.

### 5. Установи зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Создай `.env`

Скопируй пример:

```bash
cp .env.example .env
```

Открой `.env` в редакторе. Например, через VS Code:

```bash
code .env
```

Или через стандартный редактор nano:

```bash
nano .env
```

Минимум нужно заполнить:

```env
BOT_TOKEN=твой_токен_от_BotFather
```

Если хочешь, чтобы обращения приходили в служебный чат, укажи:

```env
ADMIN_CHAT_ID=-1001234567890
```

### 7. Положи реальные файлы

Замени заглушки в этих папках:

- `files/images/director.jpg`
- `files/pdf/about_company.pdf`
- `files/presentations/block_1_safety.pdf`
- `files/presentations/block_2_communications.pdf`
- `files/presentations/block_3_hr.pdf`
- `files/presentations/block_4_useful_info.pdf`
- `files/presentations/block_5_union.pdf`
- `files/presentations/block_6_services.pdf`

Важно: имена файлов должны остаться такими же, либо измени пути в `config.py`.

### 8. Отредактируй тексты

Все тексты вынесены в `texts.py`.

Там можно поменять:
- приветствие
- подписи кнопок
- тексты блоков
- текст финального меню
- текст веток “ошибка” и “сообщить или спросить”

### 9. Запусти бота

```bash
python3 main.py
```

Если всё в порядке, бот начнет работать в polling-режиме.

### 10. Как остановить

В терминале нажми:

```text
Control + C
```

### 11. Как запустить повторно

Каждый новый запуск:

```bash
cd /путь/к/hr_onboarding_bot_aiogram
source venv/bin/activate
python3 main.py
```

## Как получить ADMIN_CHAT_ID

1. Добавь бота в нужный чат.
2. Сделай бота администратором, если нужно писать в канал/группу.
3. Проще всего узнать chat id через временный хендлер, логирование входящих апдейтов или отдельный ID-бот.

## Как устроена БД

Файл базы данных создается автоматически:

```text
bot.sqlite3
```

Таблицы:

### `users`
- `id`
- `telegram_user_id`
- `full_name`
- `username`
- `phone`
- `created_at`
- `current_state`
- `current_request_type`

### `requests`
- `id`
- `user_id`
- `type`
- `text`
- `created_at`

### `errors`
- `id`
- `user_id`
- `text`
- `created_at`

## Полезные команды для отладки на Mac

Посмотреть файлы в папке:

```bash
ls -la
```

Проверить, создалась ли база:

```bash
ls -la bot.sqlite3
```

Открыть SQLite вручную:

```bash
sqlite3 bot.sqlite3
```

Посмотреть таблицы:

```sql
.tables
```

Посмотреть пользователей:

```sql
SELECT * FROM users;
```

Выйти из SQLite:

```sql
.quit
```

## Частые проблемы

### Ошибка `BOT_TOKEN is empty`
Не заполнен `.env` или бот запущен не из той папки.

### Ошибка `ModuleNotFoundError`
Зависимости не установлены. Повтори:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Бот не отвечает
Проверь:
- правильный ли токен
- запущен ли процесс `python3 main.py`
- не включён ли webhook у старой версии бота

## Как расширить проект

- вынести SQLite на PostgreSQL
- добавить Alembic/миграции
- перейти с хранения state в БД на гибрид FSM + DB
- подключить webhook и reverse proxy
- добавить админ-панель
- добавить загрузку контента из CMS/Google Sheets

## Важно

Проект уже готов как рабочий каркас, но перед боевым запуском нужно:
- заменить заглушки реальными файлами
- отредактировать тексты
- заполнить ссылки
- протестировать весь сценарий на реальном Telegram-аккаунте
# tgbot_case

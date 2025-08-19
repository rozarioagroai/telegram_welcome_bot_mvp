## Telegram Gate Bot (MVP)

Простой «гейт-бот» для пропуска пользователей в приватный канал Telegram через капчу и выдачу одноразовых инвайтов. Асинхронный, python-telegram-bot v20.7, SQLite (aiosqlite), конфиг через .env (pydantic-settings), готов к long polling и вебхукам.

### Мини-чек-лист запуска за вечер
1) Создайте бота у BotFather, получите `BOT_TOKEN`.
2) Создайте приватный канал, включите опцию «Restrict saving content».
3) Добавьте бота админом канала с правами на инвайты (Invite Users via Link).
4) Узнайте `CHANNEL_ID`:
   - Вариант A: укажите в `.env` `CHANNEL_USERNAME=@your_channel`, запустите бота — он сам сохранит id в БД (kv).
   - Вариант B: выполните:
     ```bash
     python -m src.utils.channel_tools --channel @your_channel
     ```
     Сохранённый id ищется и кэшируется в `kv`.
5) Скопируйте `.env.example` в `.env` и заполните поля (обязательно `BOT_TOKEN`, `CHANNEL_ID` ИЛИ `CHANNEL_USERNAME`, `CHECKLIST_URL` и т.д.).
6) Запустите локально:
   - `make dev` или `python -m src.bot_app`.
7) Проверьте deeplink: `t.me/<ваш_бот>?start=TEST`. Нажмите «I’m human», получите файл или ссылку-чеклист и кнопку реф-ссылки с `utm_content=TEST`.
8) Используйте `/getaccess` после капчи — бот выдаст одноразовый инвайт.

### Функционал
- `/start <payload>`: фиксирует источник `SOURCE` из deeplink, показывает капчу-кнопку «✅ I’m human» с TTL.
- Капча: подтверждение до дедлайна — отправка чек-листа и кнопок.
- Кнопки после капчи:
  - «Register via my link» — URL с UTM параметрами.
  - «Use /getaccess after KYC» — подсказка.
  - «I clicked register link» — лог клика (опциональный трек).
- `/getaccess`: проверка капчи, троттлинг, создание одноразовой инвайт-ссылки в приватный канал, логирование.
- Антиабьюз: троттлинг `/start` и `/getaccess`.
- Персистентность: SQLite, таблицы `users`, `events`, `invites`, `kv`. События: `start`, `captcha_ok`, `sent_checklist`, `clicked_ref`, `getaccess_issued`.
- Запуск: long polling по умолчанию, режим вебхуков через флаг `USE_WEBHOOK=true`.
- Логи: структурированные (уровень, событие, user_id, source).

### Архитектура
- `handlers`: хэндлеры Telegram.
- `services`: доменная логика (инвайты, троттлинг, ссылки, чек-лист).
- `utils`: утилиты для Telegram и инструменты канала.
- `db.py`: миграции и DAO.
- `config.py`: настройки из `.env`.
- `bot_app.py`: сборка приложения, регистрация хэндлеров.

### Установка и запуск локально
```bash
python -V  # ожидается Python 3.11+
python -m venv .venv
. .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # и заполните значения
make dev  # или python -m src.bot_app
```

Альтернативно с Docker:
```bash
docker build -t gate-bot:latest .
docker run --rm -it --env-file .env gate-bot:latest
```

### Переменные окружения
См. `.env.example` с комментариями. Ключевые:
- `BOT_TOKEN`
- `CHANNEL_ID` или `CHANNEL_USERNAME`
- `CHECKLIST_URL`
- `REF_BASE_URL`, `UTM_CAMPAIGN`
- `INVITE_TTL_SECONDS`, `CAPTCHA_TTL_SECONDS`, `START_THROTTLE_SECONDS`, `GETACCESS_THROTTLE_SECONDS`
- `USE_WEBHOOK`, `WEBHOOK_URL`, `PORT`

### Сценарий тестирования (Acceptance)
1) `make dev` (или `python -m src.bot_app`) — бот стартует.
2) Зайдите по deeplink `t.me/BOT?start=TEST` — у вас должна появиться кнопка «I’m human».
3) Нажмите — получите либо `checklist.pdf` (если файл существует в корне проекта), либо ссылку `CHECKLIST_URL`, и кнопку «Register via my link» с UTM `utm_content=TEST`.
4) `/getaccess` после капчи — одноразовая ссылка в канал. Повторный запрос раньше лимита — «Too fast, try later».
5) В БД (`bot.db`) появляются записи в `users`, `events`, `invites`.
6) `pytest` — тесты проходят.
7) Если задан `CHANNEL_USERNAME`, при первом старте в логи печатается числовой id, и он сохраняется в `kv`.

### Вебхуки
- Установите `USE_WEBHOOK=true` и `WEBHOOK_URL=https://your-app.example.com/webhook`, `PORT=8000`.
- Запускайте как web-сервис (см. Procfile `web`).

### Деплой (Railway/Render)
- Railway: создайте проект, добавьте переменные окружения из `.env.example`. Запускайте через long polling (проще) — просто основной процесс `python -m src.bot_app`.
- Render: используйте `Procfile`. Для long polling — `worker`. Для вебхуков — `web` и установите `USE_WEBHOOK=true`.
- Канал: добавьте бота админом с правом на инвайты. Если используете `CHANNEL_USERNAME`, первый старт сохранит `CHANNEL_ID` в `kv`.

### Тексты сообщений (готовые)
- После `/start`: «Нажмите кнопку, чтобы подтвердить, что вы человек.»
- Просроченная капча: «Time’s up. Send /start again.»
- После капчи: «Отправляю чек-лист. Затем зарегистрируйтесь по моей ссылке и используйте /getaccess после KYC.»
- Советы по #ad #referral: публикуя ссылку в постах указывайте `#ad`/`#referral`, используйте UTM для аналитики.

### Частые ошибки
- Бот не может создать инвайт: у бота нет прав администратора канала с правом на инвайты.
- CHANNEL_ID неизвестен: заполните `CHANNEL_ID` или используйте `CHANNEL_USERNAME` и перезапустите бота.
- Вебхуки не приходят: проверьте публичный `WEBHOOK_URL`, корректный `PORT` и `USE_WEBHOOK=true`.
- `checklist.pdf` отсутствует: бот отправит `CHECKLIST_URL`. Замените файл в корне проекта, чтобы отправлялся документ.

### Заметки
- Файл `checklist.pdf` в корне — заглушка. Можете заменить реальным PDF (тот же путь).
- Логирование: формат `[LEVEL] ts message (event=..., user_id=..., source=...)`.

Лицензия: MIT
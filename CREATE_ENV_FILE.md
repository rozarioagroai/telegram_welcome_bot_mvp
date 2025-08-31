# Создание .env файла на PythonAnywhere

## Выполните эту команду в консоли PythonAnywhere:

```bash
cd ~/telegram_welcome_bot_mvp
cat > .env << 'EOF'
# Telegram Bot Configuration
BOT_TOKEN=8029138825:AAF8LB85UCVYutA1CE2xp-wf3IVDEk-a4Ow
CHANNEL_USERNAME=@DanielleFoSol
CHECKLIST_URL=https://your-checklist-url.com
ADMIN_IDS=8049067662

# Optional settings
LOG_LEVEL=INFO
USE_WEBHOOK=false
DB_PATH=bot.db
INVITE_TTL_SECONDS=86400
CAPTCHA_TTL_SECONDS=60
START_THROTTLE_SECONDS=10
GETACCESS_THROTTLE_SECONDS=15
EOF
```

## Или создайте файл через веб-редактор:

1. Перейдите в Files в панели PythonAnywhere
2. Откройте папку `telegram_welcome_bot_mvp`
3. Создайте новый файл `.env`
4. Скопируйте содержимое:

```
BOT_TOKEN=8029138825:AAF8LB85UCVYutA1CE2xp-wf3IVDEk-a4Ow
CHANNEL_USERNAME=@DanielleFoSol
CHECKLIST_URL=https://your-checklist-url.com
ADMIN_IDS=8049067662
LOG_LEVEL=INFO
USE_WEBHOOK=false
DB_PATH=bot.db
INVITE_TTL_SECONDS=86400
CAPTCHA_TTL_SECONDS=60
START_THROTTLE_SECONDS=10
GETACCESS_THROTTLE_SECONDS=15
```

## Команда для создания задачи в PythonAnywhere:

```
python3.10 /home/JohnBill/telegram_welcome_bot_mvp/pythonanywhere_task.py
```

Настройте задачу на выполнение каждые 5 минут.

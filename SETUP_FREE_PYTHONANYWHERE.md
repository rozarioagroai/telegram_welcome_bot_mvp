# Настройка бота на бесплатной версии PythonAnywhere

## 🎯 Стратегия для бесплатного плана

На бесплатном плане PythonAnywhere бот будет работать сессиями по 45 секунд каждые 10 минут. Этого достаточно для обработки сообщений пользователей.

## 📋 Пошаговая настройка

### 1. Создание .env файла
```bash
cd ~/telegram_welcome_bot_mvp
cat > .env << 'EOF'
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
EOF
```

### 2. Тестирование локального запуска
```bash
python3.10 pythonanywhere_free.py
```

### 3. Создание Task в панели PythonAnywhere

**Перейдите в раздел "Tasks" и создайте новую задачу:**

**Базовая настройка (рекомендуется):**
- **Command**: `python3.10 /home/JohnBill/telegram_welcome_bot_mvp/pythonanywhere_free.py`
- **Hour**: `*`
- **Minute**: `*/10`

**Для более активного использования:**
- **Command**: `python3.10 /home/JohnBill/telegram_welcome_bot_mvp/pythonanywhere_free.py`
- **Hour**: `8-22`  
- **Minute**: `*/5`

### 4. Мониторинг работы

**Проверьте логи задачи:**
1. Перейдите в "Tasks"
2. Кликните на вашу задачу
3. Просмотрите "Log" для отладки

**Проверьте использование CPU seconds:**
- В дашборде PythonAnywhere смотрите "CPU seconds used today"
- Старайтесь не превышать 100 секунд в день

## ⚠️ Важные ограничения

- **1 задача максимум** на бесплатном плане
- **~100 CPU seconds в день** 
- **Бот работает сессиями**, не 24/7
- **Возможны задержки** в ответах (до 10 минут)

## 🚀 Рекомендации по оптимизации

1. **Уведомите пользователей** о возможных задержках
2. **Тестируйте в активные часы** (10-20 часов)
3. **Мониторьте CPU usage** ежедневно
4. **При превышении лимитов** - сократите частоту запуска

## 📈 Upgrade к платному плану

Если нужна стабильная работа 24/7:
- **Hacker план ($5/месяц)** - Always-On Tasks
- **Без ограничений CPU** для ботов
- **Более стабильная работа**

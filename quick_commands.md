# Быстрые команды для ручного управления ботом

## 🚀 Команды для консоли PythonAnywhere

### 1. Интерактивный тест (рекомендуется)
```bash
cd ~/telegram_welcome_bot_mvp
python3.10 manual_test.py
```

### 2. Быстрый тест (30 секунд)
```bash
cd ~/telegram_welcome_bot_mvp
timeout 30 python3.10 pythonanywhere_free.py
```

### 3. Средний тест (2 минуты)
```bash
cd ~/telegram_welcome_bot_mvp
timeout 120 python3.10 pythonanywhere_free.py
```

### 4. Проверка конфигурации
```bash
cd ~/telegram_welcome_bot_mvp
python3.10 -c "
from src.config import settings
print('BOT_TOKEN:', 'SET' if settings.BOT_TOKEN else 'NOT SET')
print('CHANNEL:', settings.CHANNEL_USERNAME)
print('ADMIN_IDS:', settings.ADMIN_IDS)
"
```

### 5. Проверка базы данных
```bash
cd ~/telegram_welcome_bot_mvp
python3.10 -c "
import sqlite3
conn = sqlite3.connect('bot.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM users')
print('Users:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM submissions')  
print('Submissions:', cur.fetchone()[0])
conn.close()
"
```

### 6. Просмотр логов последней задачи
```bash
# В веб-интерфейсе PythonAnywhere:
# Tasks → Ваша задача → Log
```

### 7. Принудительный запуск задачи
```bash
# В веб-интерфейсе PythonAnywhere:
# Tasks → Ваша задача → Run now
```

## 🔧 Отладочные команды

### Проверка переменных окружения
```bash
cd ~/telegram_welcome_bot_mvp
cat .env
```

### Проверка файлов проекта
```bash
cd ~/telegram_welcome_bot_mvp
ls -la
ls -la src/
```

### Проверка Python пути
```bash
cd ~/telegram_welcome_bot_mvp
python3.10 -c "import sys; print('\n'.join(sys.path))"
```

### Тест импортов
```bash
cd ~/telegram_welcome_bot_mvp
python3.10 -c "
try:
    from src.config import settings
    print('✅ Config OK')
    from src.db_sqlite import Database
    print('✅ Database OK')
    from telegram.ext import Application
    print('✅ Telegram OK')
except Exception as e:
    print('❌ Error:', e)
"
```

## ⚠️ Важные замечания

1. **Ограничения CPU**: Не запускайте бота слишком долго вручную
2. **Одновременный запуск**: Не запускайте вручную, когда работает задача
3. **Ctrl+C**: Используйте для остановки ручного запуска
4. **Логи**: Всегда проверяйте вывод на ошибки

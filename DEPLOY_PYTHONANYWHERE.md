# Деплой на PythonAnywhere

## Шаги для деплоя:

### 1. Загрузка кода
```bash
git clone https://github.com/your-username/tg_welcome_bot.git
cd tg_welcome_bot
```

### 2. Установка зависимостей
```bash
pip3.10 install --user -r requirements.txt
```

### 3. Настройка переменных окружения
Создайте файл `.env` в корне проекта:
```bash
cp config.env.example .env
nano .env
```

Заполните реальные значения:
```
BOT_TOKEN=your_real_bot_token
CHANNEL_USERNAME=@your_channel
CHECKLIST_URL=https://your-checklist-url.com
ADMIN_IDS=123456789,987654321
```

### 4. Создание задачи (Task)
1. Перейдите в раздел "Tasks" в панели PythonAnywhere
2. Создайте новую задачу с командой:
```
python3.10 /home/yourusername/tg_welcome_bot/pythonanywhere_task.py
```
3. Замените `yourusername` на ваш username
4. Установите интервал выполнения (например, каждые 5 минут)

### 5. Обновление pythonanywhere_task.py
Отредактируйте файл `pythonanywhere_task.py` и замените `yourusername` на ваш реальный username PythonAnywhere.

### 6. Запуск
Задача будет автоматически запускаться по расписанию. Для ручного запуска:
```bash
python3.10 pythonanywhere_task.py
```

## Важные моменты:

1. **Бесплатный аккаунт**: Ограничен одной задачей, которая может работать постоянно
2. **Логи**: Проверяйте логи в разделе "Tasks" для отладки
3. **Обновления**: После изменения кода делайте `git pull` и перезапускайте задачу
4. **База данных**: SQLite файл будет создан автоматически в директории проекта

## Альтернативный запуск (Always-On Tasks - платный аккаунт):
Если у вас платный аккаунт, можете использовать Always-On Tasks:
```
python3.10 /home/yourusername/tg_welcome_bot/run_bot.py
```

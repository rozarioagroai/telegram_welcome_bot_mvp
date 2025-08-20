# Развертывание Telegram Bot на Koyeb

## 🚀 Быстрый старт

### 1. Подготовка

1. **Создайте аккаунт на Koyeb**: [koyeb.com](https://koyeb.com)
2. **Убедитесь, что у вас есть токен бота** от @BotFather

### 2. Настройка переменных окружения

Отредактируйте файл `koyeb.yaml`:
```yaml
env:
  - name: BOT_TOKEN
    value: "YOUR_ACTUAL_BOT_TOKEN"
  - name: CHANNEL_USERNAME
    value: "@your_channel_username"
  - name: CHECKLIST_URL
    value: "https://your-checklist-url.com"
```

### 3. Сборка и развертывание

#### Вариант A: Через GitHub (рекомендуется)

1. **Закоммитьте изменения**:
   ```bash
   git add .
   git commit -m "Add Koyeb deployment configuration"
   git push
   ```

2. **Подключите репозиторий к Koyeb**:
   - Войдите в Koyeb Dashboard
   - Нажмите "Create App"
   - Выберите "GitHub"
   - Выберите ваш репозиторий
   - Настройте переменные окружения
   - Нажмите "Deploy"

#### Вариант B: Через Docker Hub

1. **Соберите Docker образ**:
   ```bash
   docker build -f Dockerfile.koyeb -t your-username/telegram-welcome-bot .
   ```

2. **Загрузите в Docker Hub**:
   ```bash
   docker push your-username/telegram-welcome-bot
   ```

3. **Разверните на Koyeb**:
   - Создайте новое приложение
   - Выберите "Docker"
   - Укажите образ: `your-username/telegram-welcome-bot`
   - Настройте переменные окружения
   - Разверните

### 4. Проверка работы

После развертывания:
1. **Проверьте логи** в Koyeb Dashboard
2. **Отправьте команду `/start`** боту
3. **Убедитесь, что бот отвечает**

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | Обязательная |
|------------|----------|--------------|
| `BOT_TOKEN` | Токен Telegram бота | ✅ |
| `CHANNEL_USERNAME` | Username канала | ❌ |
| `CHECKLIST_URL` | URL чек-листа | ❌ |
| `LOG_LEVEL` | Уровень логирования | ❌ |
| `USE_WEBHOOK` | Использовать webhook | ❌ (false для polling) |

### Порт

Бот работает на порту **8080** (стандарт для Koyeb).

## 📝 Логи

Логи доступны в Koyeb Dashboard:
- **Runtime logs** - логи приложения
- **Build logs** - логи сборки

## 🚨 Устранение неполадок

### Бот не отвечает

1. **Проверьте токен** - убедитесь, что `BOT_TOKEN` правильный
2. **Проверьте логи** - ищите ошибки в Koyeb Dashboard
3. **Убедитесь, что бот не заблокирован** в Telegram

### Ошибки сборки

1. **Проверьте Dockerfile** - убедитесь, что все зависимости указаны
2. **Проверьте requirements.txt** - все библиотеки должны быть совместимы
3. **Проверьте .dockerignore** - исключите ненужные файлы

### Проблемы с базой данных

1. **SQLite файлы** автоматически создаются в контейнере
2. **Для продакшена** рекомендуется использовать PostgreSQL через Koyeb Database

## 🔄 Обновления

Для обновления бота:
1. **Закоммитьте изменения** в GitHub
2. **Koyeb автоматически пересоберет** и развернет приложение
3. **Или вручную** нажмите "Redeploy" в Dashboard

## 📚 Дополнительные ресурсы

- [Koyeb Documentation](https://docs.koyeb.com/)
- [Python Telegram Bot](https://python-telegram-bot.readthedocs.io/)
- [Docker Documentation](https://docs.docker.com/)

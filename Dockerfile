# Dockerfile для VSM проекта
FROM python:3.10.0

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Создаем директории
RUN mkdir -p logs media staticfiles

# Экспонируем порт
EXPOSE 8000

# Команда по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--settings=config.settings.local"] 
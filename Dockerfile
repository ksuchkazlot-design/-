FROM python:3.12-slim

WORKDIR /app

# Копируем код (токен вшит в bot.py, env не обязателен)
COPY bot.py keys.txt ./

# Только stdlib — requirements пустой, но оставляем для надёжности
RUN touch requirements.txt && pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "bot.py"]

FROM python:3.9

WORKDIR /app

# Сначала копируем и устанавливаем зависимости
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Копируем остальное приложение
COPY . /app

CMD ["python", "app.py"]

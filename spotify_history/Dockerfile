# Используем официальную версию Airflow с Python 3.9
FROM apache/airflow:2.9.3-python3.9

# Переключаемся на пользователя airflow
USER airflow

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Если нужно, можно задать рабочую директорию (по умолчанию /opt/airflow)
WORKDIR /opt/airflow

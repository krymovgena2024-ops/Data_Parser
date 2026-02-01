# ЭТАП 1. Сборка тяжелого образа, на основе которого будет собран основной, легкий образ
FROM python:3.14-slim AS builder

# Устанавливаем системные зависимости, необходимые для сборки библиотек Python
# apt-get это менеджер пакетов для операционных систем типа Linux.
# apt-get update обновляет список доступных программ, чтобы Docker скачал самые новые версии.
# && это значит выполнить следующую команду, только если предыдущая успешно выполнилась
# -y это ответ yes на вопрос по установке системных зависимостей.
# python3-dev нужен, чтобы компилятор gcc знал, как правильно соединить код на языке C с кодом Python. libpq-dev для работы с PostgreSQL.  
# gcc это компилятор языка C, он нужен для сборки библиотек.
# rm -rf /var/lib/apt/lists/* это значит выполнить удаление папок, которые нужны только во время сборки образа, чтобы готовый образ весил меньше.
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Устанавливаем зависимости в отдельную папку
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ЭТАП 2: Финальный легкий образ
FROM python:3.14-slim

# Для работы psycopg2 в финальном образе нужна только эта  библиотека
RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем только установленные библиотеки из первого этапа
COPY --from=builder /install /usr/local

# Копируем весь остальной код проекта в контейнер
COPY . .

# Команда для запуска главного файла парсера
CMD ["python", "product_parser.py"]
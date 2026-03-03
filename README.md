# Система отслеживания самолетов (Aircraft Tracking System)

Курсовая работа по программированию на Python. Программа собирает данные о самолетах в воздушном пространстве различных стран через публичные API.

## Описание функциональности

Программа позволяет:
- Получать границы стран через API Nominatim (OpenStreetMap)
- Получать информацию о самолетах через API OpenSky Network
- Фильтровать самолеты по различным критериям
- Сохранять данные в JSON-файл
- Работать с сохраненными данными (просмотр, фильтрация, удаление)

## Технологии

- Python 3.8+
- Requests (для работы с API)
- pytest (для тестирования)

## Установка

1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/segaskypro/kursovaya_aircraft_api.git
   cd kursovaya_aircraft_api
   ```

2. Создать и активировать виртуальное окружение:
   ```bash
   python -m venv venv
   # для Windows:
   venv\Scripts\activate
   # для Linux/Mac:
   source venv/bin/activate
   ```

3. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Запустить программу:
   ```bash
   python main.py
   ```

## Структура проекта
```bash
kursovaya_aircraft_api/
│
├── api.py                 # Классы для работы с API
├── aircraft.py            # Класс самолета
├── file_handlers.py       # Классы для работы с файлами
├── main.py                # Точка входа (интерфейс)
├── test_aircraft.py       # Тесты
├── requirements.txt       # Зависимости
├── .gitignore             # Игнорируемые файлы
└── README.md              # Описание проекта
```

## Тестирование
Запуск тестов:

```bash
pytest test_aircraft.py -v
```
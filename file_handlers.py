from abc import ABC, abstractmethod
import json
import os
from typing import List, Dict, Any, Optional


class BaseFileHandler(ABC):
    """
    Абстрактный базовый класс для работы с файлами
    Определяет обязательные методы для всех классов-наследников
    """

    @abstractmethod
    def add_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Добавление данных в файл

        Args:
            data: список словарей с данными для добавления
        """
        pass

    @abstractmethod
    def get_data(self, criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Получение данных из файла по критериям

        Args:
            criteria: словарь с критериями фильтрации (ключ-значение)
                     если None - вернуть все данные

        Returns:
            список словарей с данными
        """
        pass

    @abstractmethod
    def delete_data(self, criteria: Dict[str, Any]) -> int:
        """
        Удаление данных из файла по критериям

        Args:
            criteria: словарь с критериями для удаления

        Returns:
            количество удаленных записей
        """
        pass


class JSONSaver(BaseFileHandler):
    """
    Класс для работы с JSON-файлами
    Сохраняет данные о самолетах в формате JSON
    """

    def __init__(self, filename: str = "aircrafts.json"):
        """
        Конструктор класса

        Args:
            filename: имя файла для сохранения (по умолчанию aircrafts.json)
        """
        self.__filename = filename
        self.__ensure_file_exists()

    def __ensure_file_exists(self) -> None:
        """Приватный метод для создания файла, если его нет"""
        if not os.path.exists(self.__filename):
            with open(self.__filename, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def __read_file(self) -> List[Dict[str, Any]]:
        """
        Приватный метод для чтения данных из файла

        Returns:
            список словарей из файла
        """
        try:
            with open(self.__filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Если файл пустой или поврежден, возвращаем пустой список
            return []

    def __write_file(self, data: List[Dict[str, Any]]) -> None:
        """
        Приватный метод для записи данных в файл

        Args:
            data: список словарей для записи
        """
        with open(self.__filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def __is_duplicate(self, new_item: Dict[str, Any], existing_data: List[Dict[str, Any]]) -> bool:
        """
        Проверка на дубликат по уникальным полям (callsign + время?)

        Args:
            new_item: новый элемент для проверки
            existing_data: существующие данные

        Returns:
            True если дубликат, False если нет
        """
        # Считаем самолет уникальным по callsign и стране
        # В реальном API можно добавить проверку по времени
        for item in existing_data:
            if (item.get('callsign') == new_item.get('callsign') and
                    item.get('origin_country') == new_item.get('origin_country')):
                return True
        return False

    def add_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Добавление данных в JSON-файл без дубликатов

        Args:
            data: список словарей с данными о самолетах
        """
        if not data:
            print("Нет данных для добавления")
            return

        # Читаем существующие данные
        existing_data = self.__read_file()

        # Счетчики для статистики
        added_count = 0
        duplicate_count = 0

        # Добавляем только новые данные
        for item in data:
            if not self.__is_duplicate(item, existing_data):
                existing_data.append(item)
                added_count += 1
            else:
                duplicate_count += 1

        # Если есть новые данные - записываем
        if added_count > 0:
            self.__write_file(existing_data)
            print(f"Добавлено {added_count} новых записей в {self.__filename}")
        else:
            print(f"Нет новых данных для добавления (найдено {duplicate_count} дубликатов)")

    def get_data(self, criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Получение данных из файла с фильтрацией

        Args:
            criteria: словарь с критериями, например:
                     {"origin_country": "Russia"} - все самолеты из России
                     {"velocity__gt": 200} - скорость больше 200

        Returns:
            отфильтрованный список словарей
        """
        data = self.__read_file()

        if not criteria:
            return data

        filtered_data = []
        for item in data:
            match = True

            for key, value in criteria.items():
                # Поддержка специальных операторов
                if key.endswith('__gt'):  # больше чем
                    base_key = key[:-4]
                    if base_key in item and item[base_key] <= value:
                        match = False
                        break
                elif key.endswith('__lt'):  # меньше чем
                    base_key = key[:-4]
                    if base_key in item and item[base_key] >= value:
                        match = False
                        break
                elif key.endswith('__gte'):  # больше или равно
                    base_key = key[:-5]
                    if base_key in item and item[base_key] < value:
                        match = False
                        break
                elif key.endswith('__lte'):  # меньше или равно
                    base_key = key[:-5]
                    if base_key in item and item[base_key] > value:
                        match = False
                        break
                else:  # точное совпадение
                    if key not in item or item[key] != value:
                        match = False
                        break

            if match:
                filtered_data.append(item)

        return filtered_data

    def delete_data(self, criteria: Dict[str, Any]) -> int:
        """
        Удаление данных по критериям

        Args:
            criteria: словарь с критериями для удаления

        Returns:
            количество удаленных записей
        """
        if not criteria:
            print("Ошибка: нужно указать критерии для удаления")
            return 0

        data = self.__read_file()
        initial_count = len(data)

        # Оставляем только те элементы, которые НЕ подходят под критерии
        data = [item for item in data if not all(
            item.get(k) == v for k, v in criteria.items()
        )]

        deleted_count = initial_count - len(data)

        if deleted_count > 0:
            self.__write_file(data)
            print(f"Удалено {deleted_count} записей из {self.__filename}")
        else:
            print(f"Записей по критериям {criteria} не найдено")

        return deleted_count

    @property
    def filename(self) -> str:
        """Геттер для имени файла"""
        return self.__filename


# Дополнительный класс для работы с CSV (по желанию)
class CSVHandler(BaseFileHandler):
    """
    Класс для работы с CSV-файлами
    """

    def __init__(self, filename: str = "aircrafts.csv"):
        self.__filename = filename
        # Заглушка - здесь будет реализация для CSV
        print(f"CSVHandler создан для файла {filename}")
        print("Внимание: CSVHandler пока не реализован полностью")

    def add_data(self, data: List[Dict[str, Any]]) -> None:
        """Заглушка для метода добавления"""
        print("Метод add_data для CSV пока не реализован")

    def get_data(self, criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Заглушка для метода получения"""
        print("Метод get_data для CSV пока не реализован")
        return []

    def delete_data(self, criteria: Dict[str, Any]) -> int:
        """Заглушка для метода удаления"""
        print("Метод delete_data для CSV пока не реализован")
        return 0


# Функция для преобразования объекта Aircraft в словарь
def aircraft_to_dict(aircraft) -> Dict[str, Any]:
    """
    Преобразует объект Aircraft в словарь для сохранения в JSON

    Args:
        aircraft: объект Aircraft

    Returns:
        словарь с данными самолета
    """
    return {
        'callsign': aircraft.callsign,
        'origin_country': aircraft.origin_country,
        'velocity': aircraft.velocity,
        'altitude': aircraft.altitude,
        'longitude': aircraft.longitude,
        'latitude': aircraft.latitude
    }


# Тестирование класса
if __name__ == "__main__":
    print("Тестирование JSONSaver:")
    print("-" * 50)

    # Создаем тестовые данные
    test_data = [
        {
            'callsign': 'AFL123',
            'origin_country': 'Russia',
            'velocity': 250.5,
            'altitude': 10000.0,
            'longitude': 37.5,
            'latitude': 55.5
        },
        {
            'callsign': 'UAL456',
            'origin_country': 'USA',
            'velocity': 230.0,
            'altitude': 9500.0,
            'longitude': -95.5,
            'latitude': 40.5
        }
    ]

    # Создаем экземпляр JSONSaver
    saver = JSONSaver("test_aircrafts.json")
    print(f"Файл для теста: {saver.filename}")

    # Добавляем данные
    print("\n1. Добавление данных:")
    saver.add_data(test_data)

    # Добавляем те же данные (должны отсеяться как дубликаты)
    print("\n2. Попытка добавить дубликаты:")
    saver.add_data(test_data)

    # Получаем все данные
    print("\n3. Получение всех данных:")
    all_data = saver.get_data()
    for item in all_data:
        print(f"  {item['callsign']} - {item['origin_country']} - {item['velocity']} м/с")

    # Фильтрация по стране
    print("\n4. Фильтрация по стране 'Russia':")
    russian = saver.get_data({"origin_country": "Russia"})
    for item in russian:
        print(f"  {item['callsign']}")

    # Фильтрация по скорости (больше 240)
    print("\n5. Фильтрация по скорости > 240:")
    fast = saver.get_data({"velocity__gt": 240})
    for item in fast:
        print(f"  {item['callsign']}: {item['velocity']} м/с")

    # Удаление данных
    print("\n6. Удаление данных о USA:")
    deleted = saver.delete_data({"origin_country": "USA"})

    # Проверка после удаления
    print("\n7. Данные после удаления:")
    remaining = saver.get_data()
    for item in remaining:
        print(f"  {item['callsign']}")
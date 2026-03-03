from api import AeroplanesAPI
from aircraft import Aircraft
from file_handlers import JSONSaver, aircraft_to_dict
from typing import List, Optional
import time


def print_header(text: str) -> None:
    """Выводит заголовок с рамкой"""
    print("\n" + "=" * 60)
    print(f" {text} ")
    print("=" * 60)


def print_aircraft(aircraft_list: List[Aircraft], limit: Optional[int] = None) -> None:
    """
    Вывод списка самолетов

    Args:
        aircraft_list: список самолетов
        limit: ограничение на количество выводимых самолетов
    """
    if not aircraft_list:
        print("Самолеты не найдены")
        return

    # Ограничиваем вывод, если нужно
    display_list = aircraft_list[:limit] if limit else aircraft_list

    print(f"\nНайдено самолетов: {len(aircraft_list)}")
    if limit and len(aircraft_list) > limit:
        print(f"(показаны первые {limit})")

    print("-" * 90)
    print(f"{'N':<3} {'Позывной':<12} {'Страна':<18} {'Скорость':<12} {'Высота':<12} {'Координаты':<25}")
    print("-" * 90)

    for i, a in enumerate(display_list, 1):
        # Форматируем координаты, если они есть
        if a.latitude and a.longitude:
            coords = f"{a.latitude:.2f}, {a.longitude:.2f}"
        else:
            coords = "нет данных"

        print(f"{i:<3} {a.callsign:<12} {a.origin_country:<18} "
              f"{a.velocity:<12.1f} {a.altitude:<12.1f} {coords:<25}")


def get_top_by_altitude(aircrafts: List[Aircraft], n: int) -> List[Aircraft]:
    """
    Получает топ N самолетов по высоте

    Args:
        aircrafts: список самолетов
        n: количество самолетов в топе

    Returns:
        отсортированный список
    """
    # Сортируем по высоте (от большей к меньшей)
    sorted_aircrafts = sorted(aircrafts, key=lambda x: x.altitude, reverse=True)
    return sorted_aircrafts[:n]


def filter_by_country(aircrafts: List[Aircraft], countries: List[str]) -> List[Aircraft]:
    """
    Фильтрует самолеты по стране регистрации

    Args:
        aircrafts: список самолетов
        countries: список стран для фильтрации

    Returns:
        отфильтрованный список
    """
    if not countries:
        return aircrafts

    # Приводим все к нижнему регистру для регистронезависимого поиска
    countries_lower = [c.lower().strip() for c in countries]

    filtered = []
    for a in aircrafts:
        if a.origin_country.lower() in countries_lower:
            filtered.append(a)

    return filtered


def filter_by_altitude_range(aircrafts: List[Aircraft], min_alt: float, max_alt: float) -> List[Aircraft]:
    """
    Фильтрует самолеты по диапазону высот

    Args:
        aircrafts: список самолетов
        min_alt: минимальная высота
        max_alt: максимальная высота

    Returns:
        отфильтрованный список
    """
    return [a for a in aircrafts if min_alt <= a.altitude <= max_alt]


def save_aircrafts(aircrafts: List[Aircraft], filename: str = "aircrafts.json") -> None:
    """
    Сохраняет самолеты в JSON-файл

    Args:
        aircrafts: список самолетов
        filename: имя файла
    """
    saver = JSONSaver(filename)

    # Преобразуем объекты в словари
    data = [aircraft_to_dict(a) for a in aircrafts]

    # Сохраняем
    saver.add_data(data)
    print(f"Данные сохранены в файл: {filename}")


def user_interaction() -> None:
    """
    Главная функция взаимодействия с пользователем
    """
    print_header("СИСТЕМА ОТСЛЕЖИВАНИЯ САМОЛЕТОВ")
    print("Добро пожаловать! Программа отслеживает самолеты")
    print("в воздушном пространстве различных стран.\n")

    while True:
        print("\n" + "-" * 50)
        print("ГЛАВНОЕ МЕНЮ:")
        print("1. Поиск самолетов по стране")
        print("2. Топ самолетов по высоте (из сохраненных данных)")
        print("3. Работа с сохраненными данными")
        print("4. Выход")

        choice = input("\nВыберите действие (1-4): ").strip()

        if choice == "1":
            # Поиск по стране
            print("\n" + "-" * 50)
            print("ПОИСК САМОЛЕТОВ")

            country = input("Введите название страны (например, France, Germany, Russia): ").strip()

            if not country:
                print("Ошибка: название страны не может быть пустым")
                continue

            print(f"\nЗапрашиваем данные для страны: {country}...")

            # Создаем API и получаем данные
            api = AeroplanesAPI()
            start_time = time.time()

            aeroplanes_data = api.get_data(country)

            if not aeroplanes_data:
                print(f"Не удалось получить данные для страны {country}")
                continue

            # Преобразуем в объекты
            aircrafts = Aircraft.cast_to_object_list(aeroplanes_data)

            elapsed_time = time.time() - start_time
            print(f"Данные получены за {elapsed_time:.1f} секунд")

            # Показываем результаты
            print_aircraft(aircrafts, limit=20)

            # Предлагаем действия с полученными данными
            while True:
                print("\n" + "-" * 30)
                print("ДЕЙСТВИЯ С ДАННЫМИ:")
                print("1. Топ-10 по высоте")
                print("2. Фильтр по стране регистрации")
                print("3. Фильтр по диапазону высот")
                print("4. Сохранить в файл")
                print("5. Вернуться в главное меню")

                sub_choice = input("Выберите действие: ").strip()

                if sub_choice == "1":
                    # Топ по высоте
                    top = get_top_by_altitude(aircrafts, 10)
                    print("\nТОП-10 САМОЛЕТОВ ПО ВЫСОТЕ:")
                    print_aircraft(top)

                elif sub_choice == "2":
                    # Фильтр по стране
                    countries_input = input("Введите страны через пробел (например, Russia USA Germany): ").strip()
                    countries = countries_input.split()

                    filtered = filter_by_country(aircrafts, countries)
                    print(f"\nСамолеты из стран {countries}:")
                    print_aircraft(filtered)

                elif sub_choice == "3":
                    # Фильтр по высоте
                    try:
                        min_h = float(input("Минимальная высота (м): ").strip())
                        max_h = float(input("Максимальная высота (м): ").strip())

                        filtered = filter_by_altitude_range(aircrafts, min_h, max_h)
                        print(f"\nСамолеты на высоте {min_h}-{max_h} м:")
                        print_aircraft(filtered)
                    except ValueError:
                        print("Ошибка: введите числа")

                elif sub_choice == "4":
                    # Сохранение
                    filename = input("Имя файла (по умолчанию aircrafts.json): ").strip()
                    if not filename:
                        filename = "aircrafts.json"

                    save_aircrafts(aircrafts, filename)

                elif sub_choice == "5":
                    break

                else:
                    print("Неверный выбор")

        elif choice == "2":
            # Топ самолетов из сохраненных данных
            print("\n" + "-" * 50)
            print("ТОП САМОЛЕТОВ ПО ВЫСОТЕ")

            filename = input("Имя файла с данными (по умолчанию aircrafts.json): ").strip()
            if not filename:
                filename = "aircrafts.json"

            try:
                saver = JSONSaver(filename)
                data = saver.get_data()

                if not data:
                    print("В файле нет данных")
                    continue

                # Преобразуем словари обратно в объекты
                aircrafts = []
                for item in data:
                    try:
                        a = Aircraft(
                            callsign=item.get('callsign', 'Unknown'),
                            origin_country=item.get('origin_country', 'Unknown'),
                            velocity=item.get('velocity', 0),
                            altitude=item.get('altitude', 0),
                            longitude=item.get('longitude'),
                            latitude=item.get('latitude')
                        )
                        aircrafts.append(a)
                    except (TypeError, ValueError) as e:
                        continue

                # Запрашиваем N
                try:
                    n = int(input("Сколько самолетов показать в топе? (по высоте): ").strip())
                    top = get_top_by_altitude(aircrafts, n)
                    print(f"\nТОП-{n} САМОЛЕТОВ ПО ВЫСОТЕ:")
                    print_aircraft(top)
                except ValueError:
                    print("Ошибка: введите число")

            except FileNotFoundError:
                print(f"Файл {filename} не найден")

        elif choice == "3":
            # Работа с сохраненными данными
            print("\n" + "-" * 50)
            print("РАБОТА С СОХРАНЕННЫМИ ДАННЫМИ")

            filename = input("Имя файла (по умолчанию aircrafts.json): ").strip()
            if not filename:
                filename = "aircrafts.json"

            try:
                saver = JSONSaver(filename)
                data = saver.get_data()

                print(f"\nВсего записей в файле: {len(data)}")

                # Показываем несколько примеров
                if data:
                    print("\nПримеры записей (первые 5):")
                    for i, item in enumerate(data[:5], 1):
                        print(f"  {i}. {item.get('callsign')} - {item.get('origin_country')} - "
                              f"{item.get('altitude'):.1f} м")

                # Дополнительные действия
                print("\nДЕЙСТВИЯ:")
                print("1. Удалить записи по стране")
                print("2. Поиск по стране")
                print("3. Назад")

                sub_choice = input("Выберите действие: ").strip()

                if sub_choice == "1":
                    country = input("Введите страну для удаления: ").strip()
                    if country:
                        deleted = saver.delete_data({"origin_country": country})
                        print(f"Удалено {deleted} записей")

                elif sub_choice == "2":
                    country = input("Введите страну для поиска: ").strip()
                    if country:
                        filtered = saver.get_data({"origin_country": country})
                        print(f"\nНайдено {len(filtered)} записей:")
                        for item in filtered:
                            print(f"  {item.get('callsign')} - {item.get('altitude'):.1f} м")

            except FileNotFoundError:
                print(f"Файл {filename} не найден")

        elif choice == "4":
            print("\nСпасибо за использование программы! До свидания!")
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите 1-4")


if __name__ == "__main__":
    try:
        user_interaction()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем. До свидания!")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        print("Пожалуйста, перезапустите программу.")

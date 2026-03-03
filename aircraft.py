class Aircraft:
    """
    Класс для представления информации о самолете
    Использует __slots__ для экономии памяти
    """

    __slots__ = ['__callsign', '__origin_country', '__velocity', '__altitude', '__longitude', '__latitude']

    def __init__(self, callsign, origin_country, velocity, altitude, longitude=None, latitude=None):
        """
        Конструктор класса Aircraft

        Args:
            callsign (str): Позывной самолета
            origin_country (str): Страна регистрации
            velocity (float): Скорость (м/с)
            altitude (float): Высота (м)
            longitude (float): Долгота (опционально)
            latitude (float): Широта (опционально)
        """
        # Валидация и установка значений через приватные методы
        self.__callsign = self.__validate_callsign(callsign)
        self.__origin_country = self.__validate_country(origin_country)
        self.__velocity = self.__validate_velocity(velocity)
        self.__altitude = self.__validate_altitude(altitude)
        self.__longitude = self.__validate_coordinate(longitude, -180, 180, "долгота") if longitude else None
        self.__latitude = self.__validate_coordinate(latitude, -90, 90, "широта") if latitude else None

    # ------ Приватные методы валидации ------

    def __validate_callsign(self, callsign):
        """Валидация позывного"""
        if not isinstance(callsign, str):
            raise TypeError("Позывной должен быть строкой")
        if not callsign.strip():
            raise ValueError("Позывной не может быть пустым")
        return callsign.strip()

    def __validate_country(self, country):
        """Валидация страны регистрации"""
        if not isinstance(country, str):
            raise TypeError("Страна должна быть строкой")
        if not country.strip():
            raise ValueError("Страна не может быть пустой")
        return country.strip()

    def __validate_velocity(self, velocity):
        """Валидация скорости"""
        if not isinstance(velocity, (int, float)):
            raise TypeError("Скорость должна быть числом")
        if velocity < 0:
            raise ValueError("Скорость не может быть отрицательной")
        return float(velocity)

    def __validate_altitude(self, altitude):
        """Валидация высоты"""
        if not isinstance(altitude, (int, float)):
            raise TypeError("Высота должна быть числом")
        # Высота может быть отрицательной (если самолет ниже уровня моря, но такое редко)
        # Поэтому просто преобразуем в float
        return float(altitude)

    def __validate_coordinate(self, coord, min_val, max_val, coord_name):
        """Валидация координат (широты/долготы)"""
        if not isinstance(coord, (int, float)):
            raise TypeError(f"{coord_name} должна быть числом")
        if coord < min_val or coord > max_val:
            raise ValueError(f"{coord_name} должна быть в диапазоне [{min_val}, {max_val}]")
        return float(coord)

    # ------ Геттеры (методы для доступа к приватным атрибутам) ------

    @property
    def callsign(self):
        """Получить позывной"""
        return self.__callsign

    @property
    def origin_country(self):
        """Получить страну регистрации"""
        return self.__origin_country

    @property
    def velocity(self):
        """Получить скорость"""
        return self.__velocity

    @property
    def altitude(self):
        """Получить высоту"""
        return self.__altitude

    @property
    def longitude(self):
        """Получить долготу"""
        return self.__longitude

    @property
    def latitude(self):
        """Получить широту"""
        return self.__latitude

    # ------ Магические методы для сравнения ------

    def __eq__(self, other):
        """Равны ли самолеты по скорости и высоте"""
        if not isinstance(other, Aircraft):
            return False
        return (self.velocity == other.velocity and
                self.altitude == other.altitude)

    def __lt__(self, other):
        """Меньше ли самолет по скорости (для сортировки)"""
        if not isinstance(other, Aircraft):
            raise TypeError("Нельзя сравнить самолет с другим типом")
        return self.velocity < other.velocity

    def __le__(self, other):
        """Меньше или равен по скорости"""
        if not isinstance(other, Aircraft):
            raise TypeError("Нельзя сравнить самолет с другим типом")
        return self.velocity <= other.velocity

    def __gt__(self, other):
        """Больше ли самолет по скорости"""
        if not isinstance(other, Aircraft):
            raise TypeError("Нельзя сравнить самолет с другим типом")
        return self.velocity > other.velocity

    def __ge__(self, other):
        """Больше или равен по скорости"""
        if not isinstance(other, Aircraft):
            raise TypeError("Нельзя сравнить самолет с другим типом")
        return self.velocity >= other.velocity

    # Методы для сравнения по высоте (отдельные, не магические)
    def is_higher_than(self, other):
        """Сравнение по высоте (выше ли)"""
        if not isinstance(other, Aircraft):
            raise TypeError("Нельзя сравнить самолет с другим типом")
        return self.altitude > other.altitude

    def is_lower_than(self, other):
        """Сравнение по высоте (ниже ли)"""
        if not isinstance(other, Aircraft):
            raise TypeError("Нельзя сравнить самолет с другим типом")
        return self.altitude < other.altitude

    # ------ Метод для создания объектов из данных API ------

    @classmethod
    def cast_to_object_list(cls, aeroplanes_data):
        """
        Преобразует список данных от API в список объектов Aircraft

        Args:
            aeroplanes_data: список данных от opensky API (states)

        Returns:
            list: список объектов Aircraft
        """
        aircrafts = []

        if not aeroplanes_data:
            return aircrafts

        for data in aeroplanes_data:
            try:
                # Формат данных от opensky:
                # [icao24, callsign, origin_country, time_position, last_contact,
                #  longitude, latitude, altitude, on_ground, velocity, heading,
                #  vertical_rate, sensors, altitude, transponder_code, spi_position]

                callsign = data[1] if len(data) > 1 and data[1] else "Unknown"
                origin_country = data[2] if len(data) > 2 and data[2] else "Unknown"
                velocity = data[9] if len(data) > 9 and data[9] is not None else 0.0
                altitude = data[7] if len(data) > 7 and data[7] is not None else 0.0
                longitude = data[5] if len(data) > 5 else None
                latitude = data[6] if len(data) > 6 else None

                # Создаем объект самолета
                aircraft = cls(
                    callsign=callsign.strip() if callsign else "Unknown",
                    origin_country=origin_country.strip() if origin_country else "Unknown",
                    velocity=velocity,
                    altitude=altitude,
                    longitude=longitude,
                    latitude=latitude
                )
                aircrafts.append(aircraft)

            except (TypeError, ValueError, IndexError) as e:
                # Пропускаем самолеты с ошибками в данных
                print(f"Ошибка при создании самолета: {e}. Пропускаем...")
                continue

        return aircrafts

    # ------ Строковое представление ------

    def __str__(self):
        """Человекочитаемое представление самолета"""
        return (f"Самолет {self.callsign} (Страна: {self.origin_country}) | "
                f"Скорость: {self.velocity:.1f} м/с | Высота: {self.altitude:.1f} м")

    def __repr__(self):
        """Представление для отладки"""
        return f"Aircraft('{self.callsign}', '{self.origin_country}', {self.velocity}, {self.altitude})"


# Небольшой тест для проверки работы класса
if __name__ == "__main__":
    print("Тестирование класса Aircraft:")
    print("-" * 50)

    # Создаем несколько самолетов
    a1 = Aircraft("AFL123", "Russia", 250.5, 10000.0)
    a2 = Aircraft("UAL456", "USA", 230.0, 9500.0)
    a3 = Aircraft("BAW789", "UK", 260.0, 10500.0)

    print(a1)
    print(a2)
    print(a3)

    print("\nСравнение по скорости:")
    print(f"{a1.callsign} > {a2.callsign}: {a1 > a2}")
    print(f"{a1.callsign} < {a3.callsign}: {a1 < a3}")

    print("\nСравнение по высоте:")
    print(f"{a1.callsign} выше {a2.callsign}: {a1.is_higher_than(a2)}")
    print(f"{a1.callsign} ниже {a3.callsign}: {a1.is_lower_than(a3)}")

    print("\nСортировка списка по скорости:")
    aircrafts = [a1, a2, a3]
    sorted_by_speed = sorted(aircrafts)  # Использует __lt__
    for a in sorted_by_speed:
        print(f"  {a.callsign}: {a.velocity} м/с")

    print("\nВалидация (проверка ошибок):")
    try:
        a4 = Aircraft("", "Russia", 250.5, 10000.0)  # Пустой позывной
    except ValueError as e:
        print(f"  Ошибка: {e}")
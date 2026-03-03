import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aircraft import Aircraft
from file_handlers import JSONSaver, aircraft_to_dict
from api import AeroplanesAPI

# ===== ТЕСТЫ ДЛЯ КЛАССА AIRCRAFT =====

class TestAircraft:
    """Тесты для класса Aircraft"""

    def test_aircraft_creation(self):
        """Тест создания самолета с корректными данными"""
        a = Aircraft("TEST123", "Russia", 250.5, 10000.0)
        assert a.callsign == "TEST123"
        assert a.origin_country == "Russia"
        assert a.velocity == 250.5
        assert a.altitude == 10000.0

    def test_aircraft_creation_with_coords(self):
        """Тест создания самолета с координатами"""
        a = Aircraft("TEST123", "Russia", 250.5, 10000.0, 37.5, 55.5)
        assert a.longitude == 37.5
        assert a.latitude == 55.5

    def test_empty_callsign_raises_error(self):
        """Тест: пустой позывной вызывает ошибку"""
        with pytest.raises(ValueError, match="Позывной не может быть пустым"):
            Aircraft("", "Russia", 250.5, 10000.0)

    def test_invalid_velocity_type(self):
        """Тест: неверный тип скорости вызывает ошибку"""
        with pytest.raises(TypeError, match="Скорость должна быть числом"):
            Aircraft("TEST123", "Russia", "fast", 10000.0)

    def test_negative_velocity(self):
        """Тест: отрицательная скорость вызывает ошибку"""
        with pytest.raises(ValueError, match="Скорость не может быть отрицательной"):
            Aircraft("TEST123", "Russia", -10.0, 10000.0)

    def test_comparison_by_speed(self):
        """Тест сравнения самолетов по скорости"""
        a1 = Aircraft("TEST1", "Russia", 200.0, 10000.0)
        a2 = Aircraft("TEST2", "USA", 250.0, 10000.0)

        assert a1 < a2
        assert a2 > a1
        assert a1 <= a2
        assert a2 >= a1

    def test_comparison_by_altitude(self):
        """Тест сравнения самолетов по высоте"""
        a1 = Aircraft("TEST1", "Russia", 200.0, 8000.0)
        a2 = Aircraft("TEST2", "USA", 200.0, 10000.0)

        assert a1.is_lower_than(a2)
        assert a2.is_higher_than(a1)

    def test_cast_from_api_data(self):
        """Тест преобразования данных из API в объекты"""
        # Имитация данных от API
        api_data = [
            ['4b1817', 'SWR8KW', 'Switzerland', None, None, 10.46, 47.46, 8907.78, False, 206.85],
            ['4c1817', None, 'Germany', None, None, 8.56, 50.03, 11000.0, False, 250.3]
        ]

        aircrafts = Aircraft.cast_to_object_list(api_data)

        assert len(aircrafts) == 2
        assert aircrafts[0].callsign == "SWR8KW"
        assert aircrafts[0].origin_country == "Switzerland"
        assert aircrafts[0].velocity == 206.85
        assert aircrafts[1].callsign == "Unknown"


# ===== ТЕСТЫ ДЛЯ КЛАССА JSONSAVER =====

class TestJSONSaver:
    """Тесты для класса JSONSaver"""

    def setup_method(self):
        """Подготовка перед каждым тестом"""
        self.test_filename = "test_temp.json"
        self.saver = JSONSaver(self.test_filename)

        # Очищаем файл если он существует
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def teardown_method(self):
        """Очистка после каждого теста"""
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_add_and_get_data(self):
        """Тест добавления и получения данных"""
        test_data = [
            {
                'callsign': 'TEST123',
                'origin_country': 'Russia',
                'velocity': 250.5,
                'altitude': 10000.0
            }
        ]

        self.saver.add_data(test_data)
        result = self.saver.get_data()

        assert len(result) == 1
        assert result[0]['callsign'] == 'TEST123'

    def test_no_duplicates(self):
        """Тест защиты от дубликатов"""
        test_data = [
            {
                'callsign': 'TEST123',
                'origin_country': 'Russia',
                'velocity': 250.5,
                'altitude': 10000.0
            }
        ]

        # Добавляем дважды
        self.saver.add_data(test_data)
        self.saver.add_data(test_data)

        result = self.saver.get_data()
        assert len(result) == 1

    def test_filter_by_country(self):
        """Тест фильтрации по стране"""
        test_data = [
            {'callsign': 'A1', 'origin_country': 'Russia', 'velocity': 200, 'altitude': 10000},
            {'callsign': 'A2', 'origin_country': 'USA', 'velocity': 250, 'altitude': 11000},
            {'callsign': 'A3', 'origin_country': 'Russia', 'velocity': 220, 'altitude': 9000}
        ]

        self.saver.add_data(test_data)

        filtered = self.saver.get_data({"origin_country": "Russia"})
        assert len(filtered) == 2
        assert all(item['origin_country'] == 'Russia' for item in filtered)

    def test_filter_by_velocity_gt(self):
        """Тест фильтрации по скорости (> больше чем)"""
        test_data = [
            {'callsign': 'A1', 'origin_country': 'Russia', 'velocity': 200, 'altitude': 10000},
            {'callsign': 'A2', 'origin_country': 'USA', 'velocity': 250, 'altitude': 11000},
            {'callsign': 'A3', 'origin_country': 'Germany', 'velocity': 180, 'altitude': 9000}
        ]

        self.saver.add_data(test_data)

        filtered = self.saver.get_data({"velocity__gt": 190})
        assert len(filtered) == 2
        assert all(item['velocity'] > 190 for item in filtered)

    def test_delete_by_country(self):
        """Тест удаления по стране"""
        test_data = [
            {'callsign': 'A1', 'origin_country': 'Russia', 'velocity': 200, 'altitude': 10000},
            {'callsign': 'A2', 'origin_country': 'USA', 'velocity': 250, 'altitude': 11000}
        ]

        self.saver.add_data(test_data)

        deleted = self.saver.delete_data({"origin_country": "USA"})

        assert deleted == 1
        result = self.saver.get_data()
        assert len(result) == 1
        assert result[0]['origin_country'] == 'Russia'

    def test_aircraft_to_dict(self):
        """Тест преобразования объекта Aircraft в словарь"""
        a = Aircraft("TEST123", "Russia", 250.5, 10000.0, 37.5, 55.5)
        d = aircraft_to_dict(a)

        assert d['callsign'] == "TEST123"
        assert d['origin_country'] == "Russia"
        assert d['velocity'] == 250.5
        assert d['altitude'] == 10000.0
        assert d['latitude'] == 55.5
        assert d['longitude'] == 37.5


# ===== ТЕСТЫ ДЛЯ API =====

class TestAPI:
    """Тесты для API класса"""

    def test_api_creation(self):
        """Тест создания объекта API"""
        api = AeroplanesAPI()
        assert api is not None

    def test_api_has_required_methods(self):
        """Проверка наличия обязательных методов"""
        api = AeroplanesAPI()
        assert hasattr(api, 'get_data')
        assert hasattr(api, '_connect')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
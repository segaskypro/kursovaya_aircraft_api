from abc import ABC, abstractmethod
import requests


class BaseAPI(ABC):
    """
    Абстрактный базовый класс для работы с API
    """

    def __init__(self):
        """Конструктор базового класса"""
        self.__base_url = None  # Приватный атрибут для базового URL

    @abstractmethod
    def _connect(self, endpoint):
        """
        Приватный метод для подключения к API
        Должен отправлять запрос и проверять статус-код
        """
        pass

    @abstractmethod
    def get_data(self, country_name):
        """
        Публичный метод для получения данных о самолетах по названию страны
        """
        pass


class AeroplanesAPI(BaseAPI):
    """
    Класс для работы с API nominatim.openstreetmap.org и opensky-network.org
    Наследуется от BaseAPI
    """

    def __init__(self):
        """Конструктор класса"""
        super().__init__()  # Вызываем конструктор родителя
        self.__nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.__opensky_url = "https://opensky-network.org/api/states/all"
        self.__boundingbox = None  # Здесь будем хранить границы страны

    def _connect(self, url, params=None):
        """
        Приватный метод для подключения к API
        Отправляет GET-запрос и проверяет статус-код
        """
        try:
            # Добавляем User-Agent для nominatim (требуется их правилами)
            # ВАЖНО: только английские буквы!
            headers = {
                'User-Agent': 'AeroplaneTracker/1.0 (coursework)'
            }

            response = requests.get(url, params=params, headers=headers)

            # Проверяем статус-код
            if response.status_code == 200:
                return response
            else:
                print(f"Ошибка подключения к API. Статус код: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def __get_country_boundingbox(self, country_name):
        """
        Приватный метод для получения границ страны через nominatim
        """
        # Параметры запроса к nominatim
        params = {
            'q': country_name,
            'format': 'json',
            'limit': 1
        }

        # Отправляем запрос к nominatim
        response = self._connect(self.__nominatim_url, params)

        if response and response.json():
            data = response.json()[0]
            # Получаем boundingbox из ответа
            self.__boundingbox = data.get('boundingbox')
            print(f"Границы страны {country_name}: {self.__boundingbox}")
            return True
        else:
            print(f"Не удалось найти страну: {country_name}")
            return False

    def get_data(self, country_name):
        """
        Получение информации о самолетах в воздушном пространстве страны
        """
        # Сначала получаем границы страны
        if not self.__get_country_boundingbox(country_name):
            return None

        if not self.__boundingbox:
            return None

        # Параметры для opensky (ограничиваем область поиска)
        # boundingbox имеет формат: [юг, север, запад, восток]
        params = {
            'lamin': self.__boundingbox[0],  # южная широта
            'lamax': self.__boundingbox[1],  # северная широта
            'lomin': self.__boundingbox[2],  # западная долгота
            'lomax': self.__boundingbox[3]  # восточная долгота
        }

        # Отправляем запрос к opensky
        response = self._connect(self.__opensky_url, params)

        if response:
            data = response.json()
            # В ответе нас интересует поле 'states' - список самолетов
            return data.get('states', [])
        else:
            return None


# Небольшой тест, чтобы проверить работу
if __name__ == "__main__":
    # Создаем экземпляр класса
    api = AeroplanesAPI()

    # Тестируем получение данных
    country = "France"  # Можно заменить на любую страну
    aeroplanes = api.get_data(country)

    if aeroplanes:
        print(f"\nНайдено самолетов в воздушном пространстве {country}: {len(aeroplanes)}")
        if len(aeroplanes) > 0:
            print("\nПример первого самолета:")
            print(aeroplanes[0])  # Показываем первый самолет для примера
    else:
        print("Не удалось получить данные о самолетах")
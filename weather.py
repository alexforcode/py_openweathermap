from configparser import ConfigParser
from urllib import request
from urllib import error
from urllib.parse import quote
import json
from datetime import datetime
import sys


def get_api_keys():
    """ Возвращает api key из файла config.ini для доступа к API OpenWeatherMap """
    conf = ConfigParser()
    conf.read('config.ini')
    return conf['openweathermap.org']['api_key']


def get_cities():
    """ Возвращает список городов для получения прогноза погоды """
    with open('cities.txt', 'r', encoding='utf8') as file:
        cities = file.read().splitlines()[1:]
    return cities


def get_report(cities, openweather_key):
    """
    Получает от OpenWeatherMap json с данными по городам из списка cities.
    Возвращает список кортежей вида (название города, температура, давление, восход, закат).
    """
    weather_report = []

    for city in cities:
        try:
            url = f'http://api.openweathermap.org/data/2.5/weather?q={quote(city)}&units=metric&appid={openweather_key}'
            response = request.urlopen(url)
        except error.HTTPError as err:
            if err.code == 404:
                print(f'Ошибка получения данных для города: {city}')
                continue
        except error.URLError as _:
            print('Ошибка соединения. Завершение программы.')
            sys.exit()

        data = json.loads(response.read())

        # Сдвиг UTC для получения времени 'по Москве'
        utc_offset = 10800

        # Ковертируем давление из Па в мм рт ст
        pressure = int(data['main']['pressure'] * 0.75)
        # Перевод времени из UTC в формат ЧЧ:ММ
        sunrise = datetime.utcfromtimestamp(data['sys']['sunrise'] + utc_offset).strftime('%H:%M')
        sunset = datetime.utcfromtimestamp(data['sys']['sunset'] + utc_offset).strftime('%H:%M')

        weather_report.append((city,
                               int(data['main']['temp']),
                               pressure,
                               sunrise,
                               sunset))
    return weather_report


def print_to_console(report):
    """ Выводит прогноз погоды в консоль. """
    print(f'Информация о погоде на {datetime.now().strftime("%d.%m.%Y")}')
    print('-' * 70)
    print(f'| {"Город":13}| {"Температура, С":16}| {"Давление":10}| {"Восход":10}| {"Закат":10}|')
    print('-' * 70)
    for city_data in report:
        name, t, pressure, sunrise, sunset = city_data
        print(f'| {name:13}| {t:^16d}| {pressure:^10.0f}| {sunrise:10}| {sunset:10}|')
        print('-' * 70)


def main():
    openweather_key = get_api_keys()
    cities = get_cities()
    report = get_report(cities, openweather_key)
    print_to_console(report)


if __name__ == '__main__':
    main()

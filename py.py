
import telebot
from telebot import types
import json
import requests

bot = telebot.TeleBot('6786588724:AAELwRgO4U02eXBHIXaRS_TKWXgReeloGRU')
API = '1dd938b91597cf0c13cf2f190d95b3eb'

user_state = {}  # Словарь для хранения последнего выбора пользователя

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Текущая погода')
    btn2 = types.KeyboardButton('Аналитика погоды на 16 дней')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Выберите опцию:', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id

    if message.text == 'Текущая погода':
        user_state[user_id] = 'current_weather'
        bot.send_message(message.chat.id, 'Введите название города:')
    elif message.text == 'Аналитика погоды на 16 дней':
        user_state[user_id] = 'weather_forecast'
        bot.send_message(message.chat.id, 'Введите название города для аналитики:')
    else:
        if user_id in user_state:
            if user_state[user_id] == 'current_weather':
                get_current_weather(message)
            elif user_state[user_id] == 'weather_forecast':
                get_weather_forecast(message)
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, выберите опцию.')

def get_current_weather(message):
    city = message.text.strip().lower()
    try:
        res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
        if res.status_code == 200:
            data = json.loads(res.text)
            temp = data["main"]["temp"]
            bot.reply_to(message, f'Сейчас погода в {city}: {temp}°C')
        else:
            bot.reply_to(message, 'Не удалось получить информацию о погоде для данного города.')
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка при получении данных о погоде.')

def get_weather_forecast(message):
    city = message.text.strip().lower()
    cnt = 16  # Количество дней для прогноза

    try:
        url = f'http://api.openweathermap.org/data/2.5/forecast/daily?q={city}&cnt={cnt}&appid={API}&units=metric'
        print(f"URL запроса: {url}")  # Логирование URL запроса
        res = requests.get(url)
        if res.status_code == 200:
            forecast_data = json.loads(res.text)
            send_forecast_to_user(message, forecast_data)
        else:
            print(f"Ошибка API: {res.status_code}, {res.text}")
            bot.reply_to(message, f'Ошибка при запросе данных: {res.text}')
    except Exception as e:
        print(f"Исключение: {e}")
        bot.reply_to(message, f'Произошла внутренняя ошибка: {e}')

def process_forecast_data(forecast_data):
    total_temp, max_temp, min_temp = 0, -float('inf'), float('inf')
    for day in forecast_data['list']:
        temp = day['temp']['day']
        total_temp += temp
        max_temp = max(max_temp, day['temp']['max'])
        min_temp = min(min_temp, day['temp']['min'])
    
    average_temp = total_temp / len(forecast_data['list'])
    return average_temp, max_temp, min_temp

def send_forecast_to_user(message, forecast_data):
    try:
        average_temp, max_temp, min_temp = process_forecast_data(forecast_data)
        forecast_message = (
            f"Прогноз погоды на 16 дней для {message.text}:\n"
            f"Средняя температура: {average_temp:.1f}°C\n"
            f"Максимальная температура: {max_temp:.1f}°C\n"
            f"Минимальная температура: {min_temp:.1f}°C"
        )
        bot.reply_to(message, forecast_message)
    except Exception as e:
        print(f"Ошибка обработки данных: {e}")
        bot.reply_to(message, 'Произошла ошибка при обработке данных прогноза.')


bot.polling(none_stop=True)
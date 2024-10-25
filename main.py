import requests
from bs4 import BeautifulSoup
import telebot
import json
from datetime import datetime

TOKEN = '7737186245:AAHz3qVUNim8TuPiRD-Zvl-R5eIwxAbo1qU'
bot = telebot.TeleBot(TOKEN)


def get_steamid(profileurl: str):
    url = f'https://findsteamid.com/steamid/{profileurl}'
    response = requests.get(url)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        data = soup.find_all('span', class_='text-orange-400')
        steamid = data[2].text

        grust_response = requests.get(f'https://grust.co/api/users/{steamid}')

        if grust_response.status_code == 200:
            data = grust_response.text
            json_data = json.loads(data)
            if json_data["data"] is None:
                raise Exception('Пользователь не играл в grust')

            lastseen = json_data["data"]["lastseen"]
            playtime = json_data["data"]["playtime"]
            firstjoin = json_data["data"]["firstjoin"]

            if isinstance(lastseen, int) and isinstance(playtime, int) and isinstance(firstjoin, int):
                lastseen_datetime = datetime.fromtimestamp(lastseen)
                now = datetime.now()
                days_ago = (now - lastseen_datetime).days

                firstjoin_datetime = datetime.fromtimestamp(firstjoin)
                firstjoin_days_ago = (now - firstjoin_datetime).days

                banned = "Да" if json_data["data"]["banned"] else "Нет"

                return f'Имя: {json_data["data"]["name"]}\n' \
                    f'Бан: {banned}\n' \
                    f'Последний раз был: {days_ago} дней назад\n' \
                    f'Время в игре: {int(round(playtime / 3600, 0))} часов\n' \
                    f'Присоединился: {firstjoin_days_ago} дней назад\n'\
                    f'Scrapcoins: {json_data["data"]["scrapcoins"]} 💰\n'\
                    f'STEAMID64: {steamid}\n' \
                    f'Роль: {json_data["data"]["rank"]}\n'
            else:
                return "Ошибка: Некоторые значения не являются числами."
        else:
            return f"Ошибка: Не удалось получить данные от API Grust. Код ответа: {grust_response.status_code}"
    else:
        return f"Ошибка: Не удалось получить данные от API FindSteamID. Код ответа: {response.status_code}"


@bot.message_handler(content_types=['text'])
def text_message(message):
    profile_url = message.text
    try:
        steam_url = get_steamid(profile_url)
        bot.send_message(message.chat.id, steam_url)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: неверный Steam id")


@bot.message_handler(new_chat_members=['BubueBot'])
def welcome_message(message):
    welcome_text = "Привет! Отправь мне стим айди в любом формате или кастомный название профиля получи информацию о профиле в граст."
    bot.send_message(message.chat.id, welcome_text)


if __name__ == '__main__':
    bot.polling(non_stop=True)

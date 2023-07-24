import telebot
import requests
from config import TOKEN
from tts import TTS
import random
from datetime import datetime
import re
import os

def remove_punctuation(text):
    pattern = r"[^a-zA-Zа-яА-Я0-9]"
    return re.sub(pattern, "", text)

tts = TTS()

bot = telebot.TeleBot(TOKEN)

tts = TTS()
API_URL = 'https://jokechat.ru/api/jokes/{}'

bot = telebot.TeleBot(TOKEN)

def get_joke(id):
    url = API_URL.format(id)
    response = requests.get(url)
    if response.status_code == 200:
        joke_data = response.json()
        return joke_data['joke']
    else:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Вещай!")

@bot.message_handler(commands=['joke'])
def send_joke(message):
    joke_id = random.randint(1, 46000)
    joke = get_joke(joke_id)
    
    if joke:
        audio_file = tts.text_to_ogg(joke, f"{joke_id}.ogg")
        with open(audio_file, 'rb') as audio:
            bot.send_voice(message.chat.id, audio)
    else:
        bot.send_message(message.chat.id, "Ошибка подключения к серверу :(")

@bot.message_handler(func=lambda message: True)
def send_voice_message(message):
    try:
        processed_text = remove_punctuation(message.text)
        bot.send_chat_action(message.chat.id, 'typing')
        start_time = datetime.now()
        audio_file = tts.text_to_ogg(processed_text, f"{start_time}.ogg")
        with open(audio_file, 'rb') as audio:
            bot.send_voice(message.chat.id, audio)
            duration = datetime.now() - start_time
            bot.send_message(message.chat.id, f"<b>Ты ждал это:</b> {duration}", parse_mode='HTML')
        os.remove(audio_file)    
    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(message.chat.id, "Прости, я умею озвучивать киррилицу и /joke \n Попробуй еще раз!")

bot.infinity_polling()
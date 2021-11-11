from boll import Boll, SymbolsWithBoll
import requests
from os import environ
from flask import Flask
# from config import BOT_TOKEN, CHAT_IDS

bot_token = environ['BOT_TOKEN']
chat_ids = environ['CHAT_IDS']

class Telegram:
    @staticmethod
    def telegram_bot_sendtext(bot_message, chat_id):
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + bot_message

        response = requests.get(send_text)

        return response.json()

    # @staticmethod
    # def get_chat_ids():
    #     update_url = "https://api.telegram.org/bot{}/getUpdates".format(bot_token)
    #     data = requests.get(update_url).json()
    #     print(data)
    #     return

    @staticmethod
    def send_text_to_all_static_chats():
        global chat_ids
        msg = SymbolsWithBoll().generate_msg()
        if not isinstance(chat_ids, list):
            chat_ids = chat_ids.split(',')
        for chat_id in chat_ids:
            Telegram.telegram_bot_sendtext(msg, chat_id)
        return msg

@app.route('/')
def home():
    return Telegram.send_text_to_all_static_chats()

app = Flask(__name__)
app.run(environ.get('PORT'))

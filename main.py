import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

API_TOKEN = '1731109146:AAFYwi3RizyY1Fw_aaUa2Ta-2DDMTbpD6Zg'

bot = telebot.TeleBot(API_TOKEN)

def list_view(list):
    str=""
    for x in list:
        str+=x+"\n"
    return str

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Benvenuto sono BraccinoBot\
""")

@bot.message_handler(commands=['routine'])
def nome(message):
    bot.send_message(message.chat.id,"Routin", reply_markup=routine_markup())

def routine_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('R1', callback_data="R1"),
                               InlineKeyboardButton('R2', callback_data="R2"),
                               InlineKeyboardButton(u'\U0000274c', callback_data="esci"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    if call.data == "esci":
        bot.delete_message(call.message.chat.id,call.message.id)




bot.polling()

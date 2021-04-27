import telebot
import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardMarkup,KeyboardButton
import re

API_TOKEN = '1731109146:AAFYwi3RizyY1Fw_aaUa2Ta-2DDMTbpD6Zg'

bot = telebot.TeleBot(API_TOKEN)

pos=0

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

def step_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('S1', callback_data="S1"),
                               InlineKeyboardButton('S2', callback_data="S2"),
                               InlineKeyboardButton("<==", callback_data="backRoutine"))
    return markup

def m_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('M1', callback_data="M1"),
                               InlineKeyboardButton('M2', callback_data="M2"),
                               InlineKeyboardButton("<==", callback_data="backStep"))
    return markup

def back_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("<==", callback_data="backM"))
    return markup

def mod_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("-5", callback_data="-5"),InlineKeyboardButton("+5", callback_data="+5"),InlineKeyboardButton("-10", callback_data="-10"),InlineKeyboardButton("+10", callback_data="+10"),InlineKeyboardButton("-30", callback_data="-30"),InlineKeyboardButton("+30", callback_data="+30"),InlineKeyboardButton("<==", callback_data="backM"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global pos

    if call.data == "esci":
        bot.delete_message(call.message.chat.id,call.message.id)

    if call.data == "backRoutine":
        bot.edit_message_text(chat_id=call.message.chat.id, text="Routine",reply_markup=routine_markup(), message_id=call.message.id)

    if call.data == "backStep":
        bot.edit_message_text(chat_id=call.message.chat.id, text="Steps Routine 1",reply_markup=step_markup(), message_id=call.message.id)

    if call.data == "backM":
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizioni step 1",reply_markup=m_markup(), message_id=call.message.id)
    
    if call.data == "R1":
        bot.edit_message_text(chat_id=call.message.chat.id, text="Steps Routine 1",reply_markup=step_markup(), message_id=call.message.id)

    if call.data == "S1":
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizioni step 1",reply_markup=m_markup(), message_id=call.message.id)
    
    if call.data =="M1":
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizione M1: "+ str(pos),reply_markup=mod_markup(),message_id=call.message.id)
        
    if call.data=="-5":
        pos-=5
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizione M1: "+ str(pos),reply_markup=mod_markup(),message_id=call.message.id)
        
    if call.data=="+5":
        pos+=5
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizione M1: "+ str(pos),reply_markup=mod_markup(),message_id=call.message.id)
        
    if call.data=="-10":
        pos-=10
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizione M1: "+ str(pos),reply_markup=mod_markup(),message_id=call.message.id)

    if call.data=="+10":
        pos+=10
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizione M1: "+ str(pos),reply_markup=mod_markup(),message_id=call.message.id)

    if call.data=="-30":
        pos-=30
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizione M1: "+ str(pos),reply_markup=mod_markup(),message_id=call.message.id)

    if call.data=="+30":
        pos+=30
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizione M1: "+ str(pos),reply_markup=mod_markup(),message_id=call.message.id)
        

bot.polling()

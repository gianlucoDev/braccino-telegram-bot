import telebot
import requests
import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import re

API_TOKEN = '1731109146:AAFYwi3RizyY1Fw_aaUa2Ta-2DDMTbpD6Zg'

bot = telebot.TeleBot(API_TOKEN)


routines = [
    {
        "id": 1,
        "name": "giacomo",
        "steps": [
            {
                "delay": 1000,
                "m1": 1,
                "m2": 1,
                "m3": 1,
                "m4": 1,
                "m5": 1,
                "m6": 1,
            },
            {
                "delay": 1000,
                "m1": 1,
                "m2": 1,
                "m3": 1,
                "m4": 1,
                "m5": 1,
                "m6": 1,
            }
        ]
    }
]



premutoR = ""
premutoS = ""
premutoM = ""


def list_view(list):
    str = ""
    for x in list:
        str += x+"\n"
    return str

# Handle '/start' and '/help'


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Benvenuto sono BraccinoBot\
""")


@bot.message_handler(commands=['routine'])
def nome(message):
    bot.send_message(message.chat.id, "Routine",
                     reply_markup=routinelist_markup())

# Finito


def routinelist_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    r = requests.get('http://127.0.0.1:8000/routines').json()
    routine_button = []
    for routine in r:
        routine_button.append(InlineKeyboardButton(
            routine["name"], callback_data="R"+str(routine["id"])))

    markup.add(*routine_button)
    markup.add(InlineKeyboardButton(u'\U0000274c', callback_data="esci"))

    return markup


def routine_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Avvia', callback_data="avvia"),
               InlineKeyboardButton('Modifica', callback_data="stepModifica"),
               InlineKeyboardButton("<==", callback_data="backRoutinelist"))
    return markup

# Lista step finito


def step_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2

    r_id = premutoR.replace('R', '')
    r = requests.get('http://127.0.0.1:8000/routines/'+r_id).json()
    step_button = []
    for i, step in enumerate(r["steps"]):
        step_button.append(InlineKeyboardButton(
            "S"+str(i+1), callback_data="S"+str(i+1)))

    markup.add(*step_button)
    markup.add(InlineKeyboardButton("<==", callback_data="backRoutine"))
    return markup


def m_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('M1', callback_data='m1'),
               InlineKeyboardButton('M2', callback_data="m2"),
               InlineKeyboardButton('M3', callback_data="m3"),
               InlineKeyboardButton('M4', callback_data="m4"),
               InlineKeyboardButton('M5', callback_data="m5"),
               InlineKeyboardButton('M6', callback_data="m6"),
               InlineKeyboardButton(
                   'Conferma', callback_data="confermaModifica"),
               InlineKeyboardButton("<==", callback_data="backStep"))
    return markup


def mod_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("-5", callback_data="-5"), InlineKeyboardButton("+5", callback_data="+5"), InlineKeyboardButton("-10", callback_data="-10"), InlineKeyboardButton("+10",
               callback_data="+10"), InlineKeyboardButton("-30", callback_data="-30"), InlineKeyboardButton("+30", callback_data="+30"), InlineKeyboardButton("<==", callback_data="backM"))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global M, premutoM, premutoS, premutoR

    if call.data == "esci":
        bot.delete_message(call.message.chat.id, call.message.id)

    # Torna alla lista delle routine finito
    if call.data == "backRoutinelist":
        bot.edit_message_text(chat_id=call.message.chat.id, text="Routine",
                              reply_markup=routinelist_markup(), message_id=call.message.id)

    # Torna alla routine Finito
    if call.data == "backRoutine":
        r_id = premutoR.replace('R', '')
        r = requests.get('http://127.0.0.1:8000/routines/'+r_id).json()
        bot.edit_message_text(chat_id=call.message.chat.id, text="Routine " +
                              r["name"], reply_markup=routine_markup(), message_id=call.message.id)

    if call.data == "backStep":
        r_id = premutoR.replace('R', '')
        r = requests.get('http://127.0.0.1:8000/routines/'+r_id).json()
        bot.edit_message_text(chat_id=call.message.chat.id, text="Step Routine " +
                              r["name"], reply_markup=step_markup(), message_id=call.message.id)

    if call.data == "backM":
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizioni step 1",
                              reply_markup=m_markup(), message_id=call.message.id)

    # Scelta routine finito
    if call.data.startswith("R"):
        premutoR = call.data
        r_id = call.data.replace('R', '')
        r = requests.get('http://127.0.0.1:8000/routines/'+r_id).json()
        bot.edit_message_text(chat_id=call.message.chat.id, text="Routine " +
                              r["name"], reply_markup=routine_markup(), message_id=call.message.id)

    # Pulsante modifica finito
    if call.data == "stepModifica":
        r_id = premutoR.replace('R', '')
        r = requests.get('http://127.0.0.1:8000/routines/'+r_id).json()
        bot.edit_message_text(chat_id=call.message.chat.id, text="Step Routine " +
                              r["name"], reply_markup=step_markup(), message_id=call.message.id)

    if call.data.startswith("S"):
        premutoS = call.data
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizioni " +
                              call.data, reply_markup=m_markup(), message_id=call.message.id)

    if call.data.startswith("m"):
        premutoM = call.data
        s_pos = int(premutoS.replace('S', ''))-1
        r_id = premutoR.replace('R', '')

        s = requests.get('http://127.0.0.1:8000/routines/'+r_id).json()
        m_value = s['steps'][s_pos][call.data]
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizione " + call.data +
                              ": " + str(m_value), reply_markup=mod_markup(), message_id=call.message.id)

    if call.data.startswith("+") or call.data.startswith("-"):
        M[premutoM] += int(call.data)
        bot.edit_message_text(chat_id=call.message.chat.id, text="Posizione " + premutoM +
                              ": " + str(M[premutoM]), reply_markup=mod_markup(), message_id=call.message.id)


bot.polling()

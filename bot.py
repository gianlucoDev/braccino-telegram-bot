import requests
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '1731109146:AAFYwi3RizyY1Fw_aaUa2Ta-2DDMTbpD6Zg'
bot = telebot.TeleBot(API_TOKEN)


def make_cb_data(action, *args):
    cb_data = [action] + list(args)
    return json.dumps(cb_data)


def get_cb_data(call):
    cb_data = json.loads(call.data)
    return cb_data[0], cb_data[1:]


def check_callback_action(action_type):
    def func(call):
        action, _ = get_cb_data(call)
        return action == action_type

    return func


@bot.message_handler(commands=['help', 'start'])
def welcome_command(message):
    bot.reply_to(message, 'Benvenuto sono BraccinoBot')


def main_menu_markup():
    routines = requests.get('http://127.0.0.1:8000/routines').json()

    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    for routine in routines:
        cb_data = make_cb_data('routine_choose', routine['id'])
        routine_button = InlineKeyboardButton(
            routine['name'], callback_data=cb_data)
        markup.add(routine_button)

    markup.add(InlineKeyboardButton(
        '❌ Chiudi', callback_data=make_cb_data('message_delete')))

    return markup


@bot.message_handler(commands=['routine'])
def main_menu_command(message):
    markup = main_menu_markup()
    bot.send_message(message.chat.id, 'Seleziona routine',
                     reply_markup=markup)


@bot.callback_query_handler(func=check_callback_action('main_menu'))
def main_menu(call):
    markup = main_menu_markup()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text='Seleziona routine', reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=check_callback_action('message_delete'))
def delete_message(call):
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=check_callback_action('routine_choose'))
def select_routine(call):
    _, [routine_id] = get_cb_data(call)
    routine = requests.get(
        f"http://127.0.0.1:8000/routines/{routine_id}").json()

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton('▶️ Avvia', callback_data=make_cb_data(
            'routine_start', routine_id)),
        InlineKeyboardButton('⚙️ Modifica', callback_data=make_cb_data(
            'routine_edit', routine_id)),
        InlineKeyboardButton("⬅️ Indietro",
                             callback_data=make_cb_data('main_menu'))
    )

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=f"Routine: {routine['name']}", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=check_callback_action('routine_edit'))
def routine_edit(call):
    _, [routine_id] = get_cb_data(call)
    routine = requests.get(
        f"http://127.0.0.1:8000/routines/{routine_id}").json()

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for i, step in enumerate(routine["steps"]):
        button = InlineKeyboardButton(f'S{i+1}', callback_data=make_cb_data(
            'step_select', routine_id, i))
        markup.add(button)

    markup.add(InlineKeyboardButton("⬅️ Indietro", callback_data=make_cb_data(
        'routine_choose', routine_id)))

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=f"Routine {routine['name']}\nSeleziona lo step da modificare:", reply_markup=markup)
    bot.answer_callback_query(call.id)


bot.polling()

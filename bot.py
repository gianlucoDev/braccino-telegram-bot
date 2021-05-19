import requests
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BASE_URL = 'http://127.0.0.1:8000'

API_TOKEN = '1731109146:AAFYwi3RizyY1Fw_aaUa2Ta-2DDMTbpD6Zg'
bot = telebot.TeleBot(API_TOKEN)

limiti = {
    'delay': {'min': 0, 'max': 100000000},
    'speed': {'min': 10, 'max': 30},
    'base': {'min': 0, 'max': 180},
    'shoulder': {'min': 15, 'max': 165},
    'elbow': {'min': 0, 'max': 180},
    'wrist_ver': {'min': 0, 'max': 180},
    'wrist_rot': {'min': 0, 'max': 180},
    'gripper': {'min': 10, 'max': 73}
}


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
    routines = requests.get(f'{BASE_URL}/routines').json()

    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    for routine in routines:
        cb_data = make_cb_data('routine_choose', routine['id'])
        routine_button = InlineKeyboardButton(
            routine['name'], callback_data=cb_data)
        markup.add(routine_button)

    markup.add(InlineKeyboardButton(
        '➕ Aggiugi', callback_data=make_cb_data('routine_add')))

    markup.add(InlineKeyboardButton(
        '❌ Chiudi', callback_data=make_cb_data('message_delete')))

    return markup


@bot.message_handler(commands=['routine'])
def main_menu_command(message):
    markup = main_menu_markup()
    bot.send_message(message.chat.id, 'Seleziona routine',
                     reply_markup=markup)


@bot.callback_query_handler(func=check_callback_action('routine_add'))
def routine_add(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text='Inserisci il nome della routine')

    @bot.message_handler(func=lambda m: True)
    def echo_all(message):
        routine = {"name": message.text,
                   "steps": []}
        requests.post(f"{BASE_URL}/routines/", json=routine)

        main_menu(call)


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
        f"{BASE_URL}/routines/{routine_id}").json()

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton('▶️ Avvia', callback_data=make_cb_data(
            'braccio_choose', routine_id)),
        InlineKeyboardButton('⚙️ Modifica', callback_data=make_cb_data(
            'routine_edit', routine_id)),
        InlineKeyboardButton("🗑️ Elimina",
                             callback_data=make_cb_data('routine_delete', routine_id)),
        InlineKeyboardButton("⬅️ Indietro",
                             callback_data=make_cb_data('main_menu'))
    )

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=f"Routine: {routine['name']}", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=check_callback_action('braccio_choose'))
def braccio_choose(call):
    _, [routine_id] = get_cb_data(call)
    bracci = requests.get(
        f"{BASE_URL}/braccio/").json()

    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    for braccio in bracci:
        cb_data = make_cb_data(
            'routine_start', routine_id, braccio['serial_number'])
        bracci_button = InlineKeyboardButton(
            braccio['name'], callback_data=cb_data)
        markup.add(bracci_button)
    markup.add(InlineKeyboardButton("⬅️ Indietro",
                                    callback_data=make_cb_data('routine_choose', routine_id)))

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=f"Scegli il braccio:", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=check_callback_action('routine_start'))
def routine_start(call):
    _, [routine_id, braccio_serial_number] = get_cb_data(call)

    requests.post(
        f'{BASE_URL}/braccio/{braccio_serial_number}/run/{routine_id}')

    call_new = call
    call_new.data = make_cb_data('routine_choose', routine_id)
    select_routine(call_new)


@bot.callback_query_handler(func=check_callback_action('routine_delete'))
def routine_delete(call):
    _, [routine_id] = get_cb_data(call)
    requests.delete(f"{BASE_URL}/routines/{routine_id}")
    main_menu(call)


@bot.callback_query_handler(func=check_callback_action('routine_edit'))
def routine_edit(call):
    _, [routine_id] = get_cb_data(call)
    routine = requests.get(
        f"{BASE_URL}/routines/{routine_id}").json()

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for i, step in enumerate(routine["steps"]):
        button = InlineKeyboardButton(f'S{i+1}', callback_data=make_cb_data(
            'step_select', routine_id, i))
        markup.add(button)

    markup.add(InlineKeyboardButton("➕ Aggiungi", callback_data=make_cb_data(
        'step_add', routine_id)))

    markup.add(InlineKeyboardButton("⬅️ Indietro", callback_data=make_cb_data(
        'routine_choose', routine_id)))

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=f"Routine {routine['name']}\nSeleziona lo step da modificare:", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=check_callback_action('step_delete'))
def step_delete(call):
    _, [routine_id, i] = get_cb_data(call)
    routine = requests.get(
        f"{BASE_URL}/routines/{routine_id}").json()
    routine['steps'].pop(i)
    requests.put(f"{BASE_URL}/routines/{routine_id}/", json=routine)
    call_new = call
    call_new.data = make_cb_data('routine_edit', routine_id)
    routine_edit(call_new)


@bot.callback_query_handler(func=check_callback_action('step_add'))
def step_add(call):
    _, [routine_id] = get_cb_data(call)
    routine = requests.get(
        f"{BASE_URL}/routines/{routine_id}").json()
    routine['steps'].append({
        "delay": 1000,
        "speed": 30,
        "base": 90,
        "shoulder": 45,
        "elbow": 180,
        "wrist_ver": 180,
        "wrist_rot": 90,
        "gripper": 10
    })
    requests.put(f"{BASE_URL}/routines/{routine_id}/", json=routine)
    routine_edit(call)


@bot.callback_query_handler(func=check_callback_action('step_select'))
def step_select(call):
    _, [routine_id, i] = get_cb_data(call)
    routine = requests.get(
        f"{BASE_URL}/routines/{routine_id}").json()

    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    markup.add(InlineKeyboardButton(
        'Delay', callback_data=make_cb_data('step_select_value', routine_id, i, 'delay')))
    markup.add(InlineKeyboardButton(
        'Speed', callback_data=make_cb_data('step_select_value', routine_id, i, 'speed')))
    markup.add(InlineKeyboardButton(
        'Base', callback_data=make_cb_data('step_select_value', routine_id, i, 'base')))
    markup.add(InlineKeyboardButton(
        'Shoulder', callback_data=make_cb_data('step_select_value', routine_id, i, 'shoulder')))
    markup.add(InlineKeyboardButton(
        'Elbow', callback_data=make_cb_data('step_select_value', routine_id, i, 'elbow')))
    markup.add(InlineKeyboardButton(
        'Wrist_ver', callback_data=make_cb_data('step_select_value', routine_id, i, 'wrist_ver')))
    markup.add(InlineKeyboardButton(
        'Wrist_rot', callback_data=make_cb_data('step_select_value', routine_id, i, 'wrist_rot')))
    markup.add(InlineKeyboardButton(
        'Gripper', callback_data=make_cb_data('step_select_value', routine_id, i, 'gripper')))
    markup.add(InlineKeyboardButton(
        "🗑️ Elimina", callback_data=make_cb_data('step_delete', routine_id, i)),)
    markup.add(InlineKeyboardButton(
        "⬅️ Indietro", callback_data=make_cb_data('routine_edit', routine_id)))

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=f"Routine {routine['name']}\n Modifica lo step {i+1}:", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=check_callback_action('step_select_value'))
def step_select_value(call):
    _, [routine_id, i, p] = get_cb_data(call)
    edit_value_markup(call, routine_id, i, p)
    bot.answer_callback_query(call.id)


def edit_value_markup(call, routine_id, i, p):
    routine = requests.get(
        f"{BASE_URL}/routines/{routine_id}").json()
    
    if p=="delay" or p=="speed":    
        value = routine['steps'][i][p]
    else:
        value = routine['steps'][i]["position"][p]

    markup = InlineKeyboardMarkup()
    markup.row_width = 2

    markup.add(InlineKeyboardButton(
        '-5', callback_data=make_cb_data('step_edit_value', routine_id, i, p, value - 5)))
    markup.add(InlineKeyboardButton(
        '+5', callback_data=make_cb_data('step_edit_value', routine_id, i, p, value + 5)))
    markup.add(InlineKeyboardButton(
        '-10', callback_data=make_cb_data('step_edit_value', routine_id, i, p, value - 10)))
    markup.add(InlineKeyboardButton(
        '+10', callback_data=make_cb_data('step_edit_value', routine_id, i, p, value + 10)))
    markup.add(InlineKeyboardButton(
        '-30', callback_data=make_cb_data('step_edit_value', routine_id, i, p, value - 30)))
    markup.add(InlineKeyboardButton(
        '+30', callback_data=make_cb_data('step_edit_value', routine_id, i, p, value + 30)))
    markup.add(InlineKeyboardButton("⬅️ Indietro", callback_data=make_cb_data(
        'step_select', routine_id, i)))

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=f"Routine {routine['name']}\n Modifica {p} dello step {i+1}:\n valore={value}", reply_markup=markup)


@bot.callback_query_handler(func=check_callback_action('step_edit_value'))
def step_edit_value(call):
    global limiti
    _, [routine_id, i, p, value] = get_cb_data(call)

    p_max = limiti[p]['max']
    p_min = limiti[p]['min']

    if value < p_min:
        value = p_min
    if value > p_max:
        value = p_max

    routine = requests.get(
        f"{BASE_URL}/routines/{routine_id}").json()

    if p=="delay" or p=="speed":    
        if value != routine['steps'][i][p]:

            routine['steps'][i][p] = value
            requests.put(
            f"{BASE_URL}/routines/{routine_id}/", json=routine)

            edit_value_markup(call, routine_id, i, p)

        elif value == routine['steps'][i][p]:
            bot.answer_callback_query(call.id, "Limite raggiunto")

        bot.answer_callback_query(call.id)


    else:
        if value != routine['steps'][i]["position"][p]:
            
            routine['steps'][i]["position"][p] = value
            requests.put(
            f"{BASE_URL}/routines/{routine_id}/", json=routine)

            edit_value_markup(call, routine_id, i, p)

        elif value == routine['steps'][i]["position"][p]:
            bot.answer_callback_query(call.id, "Limite raggiunto")

        bot.answer_callback_query(call.id)

    


bot.polling()

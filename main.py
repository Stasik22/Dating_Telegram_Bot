import telebot as tb
from telebot import types


API_TOKEN = ''

bot = tb.TeleBot(API_TOKEN)

# Saving portfolio of users
users = {}

def keyboard_reply():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button_1 = types.KeyboardButton("Створити анкету💌")
    keyboard.add(button_1)
    return keyboard


# Command /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = keyboard_reply()
    msg = bot.send_message(message.chat.id, "<b>Привіт, це тг бот знайомств, в якому ти зможеш знайти собі пару або друга</b>", parse_mode="html", reply_markup=keyboard)
    bot.register_next_step_handler(msg, create_profile)


# Creating of the portfolio
@bot.message_handler(commands=['Create_profile'])
def create_profile(message):
    bot.send_message(message.chat.id, "<b>Зачекайте, видаляємо допоміжні кнопки🔄.....</b>", reply_markup=types.ReplyKeyboardRemove(), parse_mode="html")
    msg = bot.reply_to(message, "<b>Введіть ваше ім'я:</b>", parse_mode='html')
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    chat_id = message.chat.id
    name = message.text
    users[chat_id] = {'name': name}
    msg = bot.reply_to(message, "<b>Введіть ваш вік:</b>", parse_mode='html')
    bot.register_next_step_handler(msg, process_age_step)


def process_age_step(message):
    chat_id = message.chat.id
    try:
        age = int(message.text)
        users[chat_id]['age'] = age
        msg = bot.reply_to(message, "<b>Напишіть кілька слів про себе:</b>", parse_mode='html')
        bot.register_next_step_handler(msg, process_bio_step)
    except ValueError:
        msg = bot.reply_to(message, "<b>Вік має бути числом. Введіть ваш вік ще раз:</b>", parse_mode='html')
        bot.register_next_step_handler(msg, process_age_step)


def process_bio_step(message):
    chat_id = message.chat.id
    bio = message.text
    users[chat_id]['bio'] = bio
    msg = bot.reply_to(message, "<b>Тепер надішліть свою фотографію:</b>", parse_mode='html')
    bot.register_next_step_handler(msg, process_photo_step)


def process_photo_step(message):
    chat_id = message.chat.id
    if message.content_type != 'photo':
        msg = bot.reply_to(message, "<b>Будь ласка, надішліть фотографію.</b>", parse_mode='html')
        bot.register_next_step_handler(msg, process_photo_step)
        return

    photo_file_id = message.photo[-1].file_id  # Беремо фото найвищої якості
    users[chat_id]['photo'] = photo_file_id
    bot.reply_to(message, "<b>Анкета створена!✅ Використовуйте команду <u>/show_profiles</u> для перегляду анкет інших користувачів.</b>", parse_mode='html')


# Перегляд анкет та оцінка
@bot.message_handler(commands=['show_profiles'])
def show_profiles(message):
    chat_id = message.chat.id
    if not users:
        bot.reply_to(message, "<b>Поки що немає доступних анкет, але ви можете взяти участь в нашому розіграші на сто грн, щоб дізнатися детальніше /info</b>", parse_mode='html')
        return

    for user_id, profile in users.items():
        if user_id != chat_id:  # Don't show portfolio to user which created it
            # Sending portfolio
            bot.send_message(chat_id, f"Ім'я: {profile['name']}\nВік: {profile['age']}\nПро себе: {profile['bio']}")
            bot.send_photo(chat_id, profile['photo'])

            # Creating two buttons, called like and dislike
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            like_button = types.InlineKeyboardButton(text="👍 Лайк", callback_data=f"like_{user_id}")
            dislike_button = types.InlineKeyboardButton(text="👎 Дизлайк", callback_data=f"dislike_{user_id}")
            keyboard.add(like_button, dislike_button)
            bot.send_message(chat_id, "Оцініть анкету:", reply_markup=keyboard)


# Pressing of the buttons corectly
@bot.callback_query_handler(func=lambda call: call.data.startswith("like_") or call.data.startswith("dislike_"))
def handle_vote(call):
    action, user_id = call.data.split("_")
    liker_id = call.message.chat.id  # ID of the user who send like
    if action == "like":
        bot.answer_callback_query(call.id, "Ви поставили лайк!")

        # Sending a message to a user who you send a like or  dislike
        bot.send_message(user_id, f"Ваша анкета сподобалась користувачу {users[liker_id]['name']}!")
    elif action == "dislike":
        bot.answer_callback_query(call.id, "Ви поставили дизлайк!")

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)  # Прибираємо кнопки після голосування


bot.polling(none_stop=True)

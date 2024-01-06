import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from envparse import Env
from telebot import types


env = Env()
TOKEN = env.str("TOKEN")

scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
client = gspread.authorize(creds)
sheet = client.open('test').sheet1  # Open the sheet

bot = telebot.TeleBot(TOKEN)


def get_buttons():
    markup = types.InlineKeyboardMarkup(row_width=1)

    btn1 = types.InlineKeyboardButton("FAQ (частые вопросы)", callback_data="faq")
    btn2 = types.InlineKeyboardButton("Программа воркшопа", callback_data="program")
    btn3 = types.InlineKeyboardButton("Оставить заявку на воркшоп", callback_data="apply")

    markup.add(btn1, btn2, btn3)

    return markup


@bot.message_handler(commands=["start", ])
def start(message):
    bot.reply_to(message,
                 "Желаете записаться на воркшоп по ООП или получить по нему информацию?"
                 "Тогда жмите соответствующую кнопку!",
                 reply_markup=get_buttons())


WORKSHOP_CONTENT = """
**1️⃣ Введение в ООП**
  - Определение и основные концепции ООП.
  - Исторический контекст и преимущества ООП.

**2️⃣ Основные принципы ООП**
  - Инкапсуляция: скрытие данных и поведения.
  - Наследование: повторное использование и расширение кода.
  - Полиморфизм: использование общих интерфейсов для разных типов.
  - Абстракция: упрощение сложных реальностей.

**3️⃣ Классы и Объекты**
  - Определение и создание классов.
  - Инициализация объектов (конструкторы).
  - Атрибуты (свойства) и методы (функции).

**4️⃣ Углубление в Классы и Объекты**
  - Статические методы и переменные класса.
  - Приватные и защищенные атрибуты и методы.
  - "Magic methods".

**5️⃣ Наследование в Деталях**
  - Создание подклассов.
  - Переопределение и расширение методов.
  - Множественное наследование и его особенности.

**6️⃣ Полиморфизм и Абстракция**
  - Примеры полиморфизма в Python.
  - Абстрактные базовые классы.
"""

FAQ = """
Q: Что я должен знать и уметь, чтобы быть в контексте происходящего на воркшопе?
A: Уверенно владеть IDE, уметь пользоваться основными типами данных в python (словари, списки, кортежи, множества, строки),
а также иметь представление что такое функции в Python.

Q: Сколько стоит участие в воркшопе?
A: 5300 рублей.

Q: Когда начнется воркшоп?
A: Занятия будут проходить с 22 января по понедельникам в 19 часов Мск

Q: Сколько всего занятий будет?
A: Ориентировочно 5 занятий, но их может быть больше - все будет зависеть от темпа.

Q: Будет ли вестись запись занятий?
A: Да, все записи будут выгружаться в телеграм сразу после занятия и будут доступны в чате в течение года.

Q: Будет ли домашка?
A: Да, будут предоставлены рекомендуемые к выполнению задания, а также будет проведено разборное занятие.

Q: Как оплатить участие?
A: Оставьте заявку и вам будет отправлена ссылка на оплату, почле чего вас добавят в группу.

Q: Будут ли еще потоки?
A: Пока в планах только один поток.

Q: Дается ли сертификат по итогам воркшопа?
A: Нет, поскольку это не курс, это интенсивный мастер-класс.
"""


def user_exists(user_id):
    # Search all records in the first column for the user_id
    user_ids = sheet.col_values(1)  # Assuming user_id is in the first column
    return str(user_id) in user_ids


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    markup = get_buttons()

    if call.data == "faq":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, FAQ, parse_mode="Markdown", reply_markup=markup)
    elif call.data == "program":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, WORKSHOP_CONTENT, parse_mode='Markdown', reply_markup=markup)
    elif call.data == "apply":
        user_id = call.from_user.id
        username = call.from_user.username or "No Username"
        if not user_exists(user_id):
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(call.message.chat.id, "Ваша заявка оставлена! Большое спасибо!"
                                                   "Я скоро вернусь со ссылкой на оплату.", reply_markup=markup)
            sheet.append_row([user_id, username, "Apply"])
        else:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(call.message.chat.id, "Вы уже зарегистрированы.", reply_markup=markup)


while True:
    try:
        bot.polling()
    except Exception as err:
        print(err)

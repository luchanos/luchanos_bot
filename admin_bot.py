import telebot
from telebot import types
import calendar
import datetime
from envparse import Env
from db import session_scope, Event


env = Env()
TOKEN = env.str("TOKEN")

bot = telebot.TeleBot(TOKEN)


# Function to create a calendar keyboard
def create_calendar(year, month):
    markup = types.InlineKeyboardMarkup()
    # Add month and year row
    markup.row(types.InlineKeyboardButton(calendar.month_name[month] + " " + str(year), callback_data="ignore"))
    # Add day names row
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    row = [types.InlineKeyboardButton(day, callback_data="ignore") for day in days]
    markup.row(*row)

    # Add day buttons
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                row.append(types.InlineKeyboardButton(str(day), callback_data=f"book-{year}-{month}-{day}"))
        markup.row(*row)

    # Add navigation buttons
    markup.row(
        types.InlineKeyboardButton("<", callback_data=f"prev-month-{year}-{month}"),
        types.InlineKeyboardButton(">", callback_data=f"next-month-{year}-{month}")
    )
    return markup


# Function to calculate the next month and year
def next_month(year, month):
    if month == 12:
        return year + 1, 1
    else:
        return year, month + 1


# Function to calculate the previous month and year
def prev_month(year, month):
    if month == 1:
        return year - 1, 12
    else:
        return year, month - 1


# Handler for the /start command
@bot.message_handler(commands=['start'])
def start(message):
    now = datetime.datetime.now()
    markup = create_calendar(now.year, now.month)
    bot.send_message(message.chat.id, "Choose a date:", reply_markup=markup)


# Handler for calendar callbacks
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data.startswith("book-"):
        _, year, month, day = call.data.split('-')
        bot.answer_callback_query(call.id, f"Selected date: {day}-{month}-{year}")
        booked_date = datetime.datetime(year=int(year), month=int(month), day=int(day))
        event_type = "ENGLISH_SPEAKING_CLUB"
        with session_scope() as session:
            event = Event(
                actual_date=datetime.datetime(year=int(year), month=int(month), day=int(day)),
                type=event_type,
                status="ACTIVE",
            )
            session.add(event)
            session.commit()
        booking_details = f"You have successfully booked an event {event_type} on {booked_date.strftime('%Y-%m-%d')}."
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=booking_details)

    # Handle next month navigation
    if call.data.startswith("next-month"):
        year, month = map(int, call.data.split('-')[2:])
        year, month = next_month(year, month)
        markup = create_calendar(year, month)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Choose a date:", reply_markup=markup)

    # Handle previous month navigation
    elif call.data.startswith("prev-month"):
        year, month = map(int, call.data.split('-')[2:])
        year, month = prev_month(year, month)
        markup = create_calendar(year, month)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Choose a date:", reply_markup=markup)


bot.polling()

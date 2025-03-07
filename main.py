import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import get_code_city_for_train, get_tickets_train, get_tickets_flight, get_tickets_bus

API_TOKEN = "8004301898:AAFWxdTYlD0v6iujuQEhyA46RohBQ4nmu44"

bot = telebot.TeleBot(API_TOKEN)
user_states = {}


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    btn_train = InlineKeyboardButton("🚆 بلیط قطار", callback_data="train_ticket")
    btn_plane = InlineKeyboardButton("✈️ بلیط هواپیما", callback_data="plane_ticket")
    btn_bus = InlineKeyboardButton("🚌 بلیط اتوبوس", callback_data="bus_ticket")
    markup.add(btn_train, btn_plane, btn_bus)

    bot.send_message(message.chat.id, "🎉 خوش آمدید! لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["train_ticket", "plane_ticket", "bus_ticket"])
def callback_handler(call):
    user_id = call.from_user.id
    transport_type = {
        "train_ticket": "قطار 🚆",
        "plane_ticket": "هواپیما ✈️",
        "bus_ticket": "اتوبوس 🚌"
    }[call.data]

    # Initialize user state
    user_states[user_id] = {"stage": "origin", "transport_type": transport_type}

    bot.send_message(call.message.chat.id, f"شما {transport_type} را انتخاب کردید.\n لطفاً مبدا خود را وارد کنید:")


@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_user_input(message):
    user_id = message.from_user.id

    if user_id in user_states:
        state = user_states[user_id]

        if state["stage"] == "origin":
            user_states[user_id]["origin"] = message.text
            user_states[user_id]["origin_code"] = get_code_city_for_train(city_name=message.text)
            user_states[user_id]["stage"] = "destination"
            bot.send_message(message.chat.id, "✅ مبدا دریافت شد! حالا مقصد خود را وارد کنید:")

        elif state["stage"] == "destination":
            user_states[user_id]["destination"] = message.text
            user_states[user_id]["destination_code"] = get_code_city_for_train(city_name=message.text)
            user_states[user_id]["stage"] = "date"
            bot.send_message(message.chat.id, "📆 لطفاً تاریخ سفر خود را وارد کنید (به‌صورت YYYY-MM-DD):")

        elif state["stage"] == "date":
            user_states[user_id]["date"] = message.text

            data = user_states[user_id]
            summary = f"""
        📌 **جزئیات بلیط شما**:
        🚍 نوع وسیله: {data["transport_type"]}
        🏙 مبدا: {data["origin"]}
        🌆 مقصد: {data["destination"]}
        📆 تاریخ: {data["date"]}
        
        ✅ اطلاعات شما ذخیره شد. در صورت نیاز به ویرایش، دوباره استارت بزنید.
        """
            bot.send_message(message.chat.id, summary)

            # TODO : send request for get tickets

            if state["transport_type"] == "هواپیما ✈️":
                messages = get_tickets_flight(state=state)
                for msg in messages:
                    bot.send_message(message.chat.id, msg)

            elif state["transport_type"] == "قطار 🚆":
                messages = get_tickets_train(state=state)
                for msg in messages:
                    bot.send_message(message.chat.id, msg)

            elif state["transport_type"] == "اتوبوس 🚌":
                messages = get_tickets_bus(state=state)
                for msg in messages:
                    bot.send_message(message.chat.id, msg)

            # Remove user from state tracking (reset)
            del user_states[user_id]


bot.infinity_polling()

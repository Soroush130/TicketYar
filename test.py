from telebot import TeleBot, types
import json

from scraper.ticket_flight import get_tickets_flight_from_site
from scraper.ticket_train import get_tickets_train_from_site
from scraper.ticket_bus import get_tickets_bus_from_site


# Initialize the bot with your token
API_TOKEN = "8004301898:AAFWxdTYlD0v6iujuQEhyA46RohBQ4nmu44"
bot = TeleBot(API_TOKEN)

# Dictionary to store user states
user_states = {}

summary = """
📌 **جزئیات بلیط شما**:
🚍 نوع وسیله: TRANSPORT_TYPE
🏙 مبدا: ORIGIN
🌆 مقصد: DESTINATION
📆 تاریخ: DATE

✅ اطلاعات شما ذخیره شد. در صورت نیاز به ویرایش، دوباره استارت بزنید.
"""

ticket_train_message = """
🚆 **بلیط قطار**
🏙 **مبدا**: ORIGIN
🌆 **مقصد**: DESTINATION
📅 **تاریخ حرکت**: DATESTART
🕒 **تاریخ رسیدن**: DATEEND
💰 **قیمت**: PRICE تومان
🎟 **ظرفیت**: CAPACITY نفر
"""

ticket_flight_message = """
✈️ جزئیات پرواز:
━━━━━━━━━━━━━━━━━━━
🆔 کد پرواز: FlightID
🚀 هواپیمایی: Airline
✈️ شماره پرواز: FlightNo
━━━━━━━━━━━━━━━━━━━
📍 مبدأ: Origin
📍 مقصد: Destination
━━━━━━━━━━━━━━━━━━━
⏰ زمان پرواز: DepartureTime
⏳ زمان فرود: ArrivalTime
━━━━━━━━━━━━━━━━━━━
💺 کلاس پروازی: CabinClass
🎟 ظرفیت باقی‌مانده: Capacity نفر
━━━━━━━━━━━━━━━━━━━
💰 قیمت بلیط:  
👨‍🦳 بزرگسال: AdultFare تومان  
🧒 کودک: ChildFare تومان  
👶 نوزاد: InfantFare تومان  
━━━━━━━━━━━━━━━━━━━
🧳 مقدار بار مجاز: Baggage
"""


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """
    Handles the /start and /help commands.
    Sends a welcome message with inline buttons for selecting transport type.
    """
    markup = types.InlineKeyboardMarkup()
    btn_train = types.InlineKeyboardButton("🚆 بلیط قطار", callback_data="train_ticket")
    btn_plane = types.InlineKeyboardButton("✈️ بلیط هواپیما", callback_data="plane_ticket")
    btn_bus = types.InlineKeyboardButton("🚌 بلیط اتوبوس", callback_data="bus_ticket")
    markup.add(btn_train, btn_plane, btn_bus)

    bot.send_message(message.chat.id, "🎉 خوش آمدید! لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["train_ticket", "plane_ticket", "bus_ticket"])
def callback_handler(call):
    """
    Handles the callback when a user selects a transport type.
    Initializes the user state and asks for the origin.
    """
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
    """
    Handles user input based on their current state.
    """
    user_id = message.from_user.id
    state = user_states[user_id]

    if state["stage"] == "origin":
        handle_origin_input(user_id, message)
    elif state["stage"] == "destination":
        handle_destination_input(user_id, message)
    elif state["stage"] == "date":
        handle_date_input(user_id, message)


def handle_origin_input(user_id, message):
    """
    Handles the origin input from the user.
    """
    user_states[user_id]["origin"] = message.text
    user_states[user_id]["origin_code"] = get_code_city_for_train(city_name=message.text)
    user_states[user_id]["stage"] = "destination"
    bot.send_message(message.chat.id, "✅ مبدا دریافت شد! حالا مقصد خود را وارد کنید:")


def handle_destination_input(user_id, message):
    """
    Handles the destination input from the user.
    """
    user_states[user_id]["destination"] = message.text
    user_states[user_id]["destination_code"] = get_code_city_for_train(city_name=message.text)
    user_states[user_id]["stage"] = "date"
    bot.send_message(message.chat.id, "📆 لطفاً تاریخ سفر خود را وارد کنید (به‌صورت YYYY-MM-DD):")


def handle_date_input(user_id, message):
    """
    Handles the date input from the user.
    """
    user_states[user_id]["date"] = message.text

    data = user_states[user_id]

    # Corrected the typo: .repalce() -> .replace()
    summary_msg = summary.replace("TRANSPORT_TYPE", data["transport_type"])\
        .replace("ORIGIN", data["origin"])\
        .replace("DESTINATION", data["destination"])\
        .replace("DATE", data["date"])

    bot.send_message(message.chat.id, summary_msg)

    # Fetch and send tickets based on transport type
    transport_type = data["transport_type"]
    if transport_type == "هواپیما ✈️":
        messages = get_tickets_flight(state=data)
    elif transport_type == "قطار 🚆":
        messages = get_tickets_train(state=data)
    elif transport_type == "اتوبوس 🚌":
        messages = get_tickets_bus(state=data)

    for msg in messages:
        bot.send_message(message.chat.id, msg)

    # Remove user from state tracking (reset)
    del user_states[user_id]


def get_code_city_for_train(city_name):
    """
    Placeholder function to get city code for train.
    """
    with open('city.json', "r", encoding="utf-8") as file:
        json_string = file.read()

    city_list = json.loads(json_string)
    city_information = next(city for city in city_list if city['Name'] == city_name)
    return city_information['Code']

def get_code_city_for_flight(city_name):
    data = {
        'مشهد': 'MHD',
        'تهران': 'THR',
        'اصفهان': 'IFN',
        'شیراز': 'SYZ',
        'اهواز': 'AWD',
        'تبریز': 'TBZ',
        'کرمانشاه': 'KSH',
        'کرمان': 'KER',
        'ارومیه': 'OMH',
        'زاهدان': 'ZAH',
        'رشت': 'RAS',
        'یزد': 'AZD',
        'کیش': 'KIH',
        'چابهار': 'ZBR',
        'ایلام': 'IIL',
    }

    return data[city_name]


def get_tickets_train(state):
    """
    Placeholder function to get train tickets.
    """
    messages = []
    parameters = {
        'from': str(state["origin_code"]),
        'to': str(state["destination_code"]),
        'date': str(state["date"]),
        'genderCode': '3',
        'adultCount': '1',
        'childCount': '0',
        'infantCount': '0',
        'exclusive': 'false',
        'availableStatus': 'Both',
    }
    status, tickets = get_tickets_train_from_site(parameters=parameters)
    if status:
        if tickets != []:
            for ticket in tickets:
                price = "نامشخص"
                capacity = "نامشخص"

                if "prices" in ticket and len(ticket["prices"]) > 0:
                    first_price_entry = ticket["prices"][0]

                    if "classes" in first_price_entry and len(first_price_entry["classes"]) > 0:
                        class_info = first_price_entry["classes"][0]

                        price = class_info.get("price", "نامشخص")
                        capacity = class_info.get("capacity", "نامشخص")
                
                current_ticket_message = ticket_message.replace("ORIGIN", ticket.get('fromName', 'نامشخص'))\
                    .replace("DESTINATION", ticket.get('toName', 'نامشخص'))\
                    .replace("DATESTART", convert_jalali_to_gregorian(ticket.get('departureTime', 'نامشخص')))\
                    .replace("DATEEND", convert_jalali_to_gregorian(ticket.get('arrivalTime', 'نامشخص')))\
                    .replace("PRICE", price).replace("CAPACITY", capacity)

                messages.append(current_ticket_message)
        else:
            message_text = "متاسفانه، بلیطی پیدا نشد ."
            messages.append(message_text)

        return messages
    else:
        messages.append(tickets)
        return messages


    
def get_tickets_flight(state):
    """
    Placeholder function to get flight tickets.
    """
    messages = []
    parameters = {
        "DepartureDate": str(state["date"]),
        "DestinationCode": get_code_city_for_flight(str(state["destination"])),
        "OriginCode": get_code_city_for_flight(str(state["origin"]))
    }
    status, tickets = get_tickets_flight_from_site(parameters=parameters)

    if status:
        if tickets != []:
            for ticket in tickets:
                # Create a local copy of ticket_flight_message
                current_ticket_message = ticket_flight_message.replace("FlightID", str(ticket['Flight ID']))\
                    .replace("Airline", str(ticket['Airline']))\
                    .replace("FlightNo", str(ticket['Flight No.']))\
                    .replace("Origin", str(ticket['Origin']))\
                    .replace("Destination", str(ticket['Destination']))\
                    .replace("DepartureTime", str(ticket['Departure Time']))\
                    .replace("ArrivalTime", str(ticket['Arrival Time']))\
                    .replace("CabinClass", str(ticket['Cabin Class']))\
                    .replace("Capacity", str(ticket['Capacity']))\
                    .replace("AdultFare", str(ticket['Adult Fare']))\
                    .replace("ChildFare", str(ticket['Child Fare']))\
                    .replace("InfantFare", str(ticket['Infant Fare']))\
                    .replace("Baggage", str(ticket['Baggage']))
                messages.append(current_ticket_message)
        else:
            message_text = "متاسفانه، بلیطی پیدا نشد."
            messages.append(message_text)

        return messages
    else:
        messages.append(tickets)
        return messages



def get_tickets_bus(state):
    """
    Placeholder function to get bus tickets.
    """
    # Implement your logic here
    return ["در حال حاضر امکان مشاهده بلیط های اتوبوس نیست"]


# Start the bot
bot.infinity_polling()
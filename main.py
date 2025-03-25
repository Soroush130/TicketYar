from telebot import TeleBot, types
import json

from scraper.ticket_flight import get_tickets_flight_from_site
from scraper.ticket_train import get_tickets_train_from_site
from scraper.ticket_bus import get_tickets_bus_from_site
from utils import read_city_json, register_user
from models.Users_models import User
from reports.export_xlsx import create_export_xlsx_users

API_TOKEN = "8004301898:AAFWxdTYlD0v6iujuQEhyA46RohBQ4nmu44"
bot = TeleBot(API_TOKEN)

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

# Dictionary to store user states
user_states = {}

cities_train = list(set(city.get('Name', 'Unknown') for city in read_city_json()))
cities_flight = ['مشهد','تهران','اصفهان','شیراز','اهواز','تبریز','کرمانشاه','کرمان','ارومیه','زاهدان','رشت','یزد','کیش','چابهار','ایلام']

@bot.message_handler(commands=['help'])
def get_all_users(message):
    users = User.select().order_by(User.join_date.desc())
    
    file_name = create_export_xlsx_users(users=users)
        # Send the file to the user
    with open(file_name, 'rb') as file:
        bot.send_document(message.chat.id, file)

    # Optional: Confirm after sending the file
    bot.send_message(message.chat.id, "✅ User list exported successfully!")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Register New User
    register_user(information=message)
    
    
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_train = types.InlineKeyboardButton("🚆 بلیط قطار", callback_data="train_ticket")
    btn_plane = types.InlineKeyboardButton("✈️ بلیط هواپیما", callback_data="plane_ticket")
    btn_bus = types.InlineKeyboardButton("🚌 بلیط اتوبوس", callback_data="bus_ticket")
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

    user_states[user_id] = {"stage": "origin", "transport_type": transport_type}

    send_cities(call.message.chat.id, user_id)

# Send cities (merged for origin and destination)
def send_cities(chat_id, user_id):
    transport_type = user_states[user_id]['transport_type']
    markup = types.InlineKeyboardMarkup(row_width=2)

    if transport_type == "قطار 🚆":
        for city in cities_train:
            if city != 'Unknown':
                markup.add(types.InlineKeyboardButton(city, callback_data=f"city_{city}"))

    if transport_type == "هواپیما ✈️":
        for city in cities_flight:
            if city != 'Unknown':
                markup.add(types.InlineKeyboardButton(city, callback_data=f"city_{city}"))

    if transport_type == "اتوبوس 🚌":
        pass

    bot.send_message(chat_id, "🏙 لطفاً شهر مورد نظر خود را انتخاب کنید:", reply_markup=markup)

# Handle city selection
@bot.callback_query_handler(func=lambda call: call.data.startswith("city_"))
def handle_city_selection(call):
    user_id = call.from_user.id
    city = call.data.split("_")[1]

    if user_states[user_id]['stage'] == 'origin':
        user_states[user_id]['origin'] = city
        user_states[user_id]['stage'] = 'destination'

        send_cities(call.message.chat.id, user_id)

    elif user_states[user_id]['stage'] == 'destination':
        user_states[user_id]['destination'] = city
        user_states[user_id]['stage'] = 'date'
        bot.send_message(call.message.chat.id, "📆 لطفاً تاریخ سفر خود را وارد کنید (به‌صورت YYYY-MM-DD):")

@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id]['stage'] == 'date')
def handle_date_input(message):
    user_id = message.from_user.id
    user_states[user_id]['date'] = message.text

    data = user_states[user_id]

    if data['transport_type'] == 'قطار 🚆':
        data['origin_code'] = get_code_city_for_train(data['origin'])
        data['destination_code'] = get_code_city_for_train(data['destination'])
        messages = get_tickets_train(data)
    elif data['transport_type'] == 'هواپیما ✈️':
        messages = get_tickets_flight(data)
    elif data['transport_type'] == 'اتوبوس 🚌':
        messages = get_tickets_bus(data)

    summary_msg = f"📌 **جزئیات بلیط شما**:\n🚍 نوع وسیله: {data['transport_type']}\n🏙 مبدا: {data['origin']}\n🌆 مقصد: {data['destination']}\n📆 تاریخ: {data['date']}"

    bot.send_message(message.chat.id, summary_msg)

    for msg in messages:
        bot.send_message(message.chat.id, msg)

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

bot.infinity_polling()
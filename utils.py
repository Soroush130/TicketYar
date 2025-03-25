import json
import datetime
import jdatetime

from scraper.ticket_flight import get_tickets_flight_from_site
from scraper.ticket_train import get_tickets_train_from_site
from scraper.ticket_bus import get_tickets_bus_from_site

from models.Users_models import User


def get_tickets_bus(state):
    messages = []
    parameters = {

    }
    status, tickets = get_tickets_bus_from_site(parameters=parameters)
    if status:
        pass

    else:
        messages.append(tickets)
        return messages

def get_tickets_flight(state):
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
                message_text = f"""
            ✈️ جزئیات پرواز:
            ━━━━━━━━━━━━━━━━━━━
            🆔 کد پرواز: {ticket['Flight ID']}
            🚀 هواپیمایی: {ticket['Airline']}
            ✈️ شماره پرواز: {ticket['Flight No.']}
            ━━━━━━━━━━━━━━━━━━━
            📍 مبدأ: {ticket['Origin']}  
            📍 مقصد: {ticket['Destination']}
            ━━━━━━━━━━━━━━━━━━━
            ⏰ زمان پرواز: {ticket['Departure Time']}
            ⏳ زمان فرود: {ticket['Arrival Time']}
            ━━━━━━━━━━━━━━━━━━━
            💺 کلاس پروازی: {ticket['Cabin Class']}
            🎟 ظرفیت باقی‌مانده: {ticket['Capacity']} نفر
            ━━━━━━━━━━━━━━━━━━━
            💰 قیمت بلیط:  
            👨‍🦳 بزرگسال: {ticket['Adult Fare']:,} تومان  
            🧒 کودک: {ticket['Child Fare']:,} تومان  
            👶 نوزاد: {ticket['Infant Fare']:,} تومان  
            ━━━━━━━━━━━━━━━━━━━
            🧳 مقدار بار مجاز: {ticket['Baggage']}
            """

                messages.append(message_text)
        else:
            message_text = "متاسفانه، بلیطی پیدا نشد ."
            messages.append(message_text)

        return messages
    else:
        messages.append(tickets)
        return messages


def get_tickets_train(state):
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

                ticket_message = f"""
                🚆 **بلیط قطار**
                🏙 **مبدا**: {ticket.get('fromName', 'نامشخص')}
                🌆 **مقصد**: {ticket.get('toName', 'نامشخص')}
                📅 **تاریخ حرکت**: {convert_jalali_to_gregorian(ticket.get('departureTime', 'نامشخص'))}
                🕒 **تاریخ رسیدن**: {convert_jalali_to_gregorian(ticket.get('arrivalTime', 'نامشخص'))}
                💰 **قیمت**: {price} تومان
                🎟 **ظرفیت**: {capacity} نفر
                """

                messages.append(ticket_message)
        else:
            message_text = "متاسفانه، بلیطی پیدا نشد ."
            messages.append(message_text)

        return messages
    else:
        messages.append(tickets)
        return messages


def read_city_json():
    path_file = 'city.json'
    with open(path_file, "r", encoding="utf-8") as file:
        json_string = file.read()

    data = json.loads(json_string)
    return data


def get_code_city_for_train(city_name):
    city_list = read_city_json()
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


def convert_jalali_to_gregorian(jalali_date):
    gregorian_datetime = datetime.datetime.strptime(jalali_date, "%Y-%m-%dT%H:%M:%S")
    jalali_date = jdatetime.datetime.fromgregorian(datetime=gregorian_datetime)
    return jalali_date.strftime("%Y/%m/%d - %H:%M")


def register_user(information):
    user_id = information.from_user.id
    first_name = information.from_user.first_name or ""   # Handle None
    last_name = information.from_user.last_name or ""     # Handle None
    username = information.from_user.username or f"user_{user_id}"  # Fallback for username
    language_code = information.from_user.language_code or "unknown"

    try:
        # Try to get the user from the database
        user = User.get(User.username == username, User.user_id == user_id)
        return user
    except User.DoesNotExist:
        # If user does not exist, create a new one
        user = User.create(
            username=username,
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code
        )
        return user

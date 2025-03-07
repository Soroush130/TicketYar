import requests
# from rich.console import Console
# from rich.table import Table

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

def get_tickets_flight_from_site(parameters):
    # API URL
    url = "https://flight.atighgasht.com/api/Flights"

    # Headers
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    }

    # JSON Payload
    payload = {
        "AdultCount": 1,
        "Baggage": True,
        "CabinClass": "All",
        "ChildCount": 0,
        "InfantCount": 0,
        "Routes": [
            {
                "DepartureDate": parameters['DepartureDate'],
                "DestinationCode": parameters['DestinationCode'],
                "OriginCode": parameters['OriginCode']
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        return False, "متاسفیم! در حال حاضر امکان مشاهده بلیط هواپیما وجود ندارد. دقایقی دیگر منتظرتان هستیم."

    flights = extract_flight_data(data=response.json())

    return True, flights

def extract_flight_data(data):
    flights_info = []
    for flight in data["Flights"]:
        for price in flight["Prices"]:
            segments = flight["Segments"][0]["Legs"][0]  # Taking the first segment leg
            flights_info.append({
                "Flight ID": flight["Id"],
                "Airline": segments["Airline"]["EnglishTitle"],
                "Flight No.": segments["FlightNumber"],
                "Origin": segments["Origin"],
                "Destination": segments["Destination"],
                "Departure Time": segments["DepartureTime"],
                "Arrival Time": segments["ArrivalTime"],
                "Cabin Class": price["CabinClass"],
                "Adult Fare": price["PassengerFares"][0]["TotalFare"],
                "Child Fare": price["PassengerFares"][1]["TotalFare"],
                "Infant Fare": price["PassengerFares"][2]["TotalFare"],
                "Baggage": f"{price['Baggage']} {price['BaggageType']}",
                "Capacity": price["Capacity"]
            })
    return flights_info

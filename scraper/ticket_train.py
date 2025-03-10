import requests
# from rich.console import Console
# from rich.table import Table


def get_tickets_train_from_site(parameters):
    base_url = "https://train.mrbilit.com/api/GetAvailable/v2?"

    for key, value in parameters.items():
        base_url += f"&{key}={value}"

    response = requests.get(base_url)
    print(response)
    print(response.status_code)

    if response.status_code != 200:
        return False, "متاسفیم! در حال حاضر امکان مشاهده بلیط قطار به علت عملیات پشتیبانی راه آهن وجود ندارد. دقایقی دیگر منتظرتان هستیم."

    # Extract Train Data
    Trains = response.json().get("trains", [])
    Tickets = []

    for train in Trains:
        train_number = train.get("trainNumber", "N/A")
        departure_time = train.get("departureTime", "N/A")
        arrival_time = train.get("arrivalTime", "N/A")

        for price in train.get("prices", []):
            for ticket in price.get("classes", []):
                ticket["trainNumber"] = train_number
                ticket["departureTime"] = departure_time
                ticket["arrivalTime"] = arrival_time
                Tickets.append(ticket)

    return True, Trains

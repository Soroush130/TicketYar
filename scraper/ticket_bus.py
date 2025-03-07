import requests
# from rich.console import Console
# from rich.table import Table

def get_tickets_bus_from_site(parameters):
    url = "https://bus.mrbilit.ir/api/GetBusServices"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    }

    payload = {
        "date": "2025-02-10",
        "from": 11320000,
        "to": 87330000,
        "includeClosed": True,
        "includePromotions": True,
        "includeUnderDevelopment": True,
        "loadFromDbOnUnavailability": True,
    }

    # Sending Request
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        return False, "متاسفیم! در حال حاضر امکان مشاهده بلیط اتوبوس وجود ندارد. دقایقی دیگر منتظرتان هستیم."


    buses = extract_buses_data(data=response.json())

    return True, buses

def extract_buses_data(data):
    buses = data.get("buses", [])

    return buses


# # API URL
# url = "https://bus.mrbilit.ir/api/GetBusServices"
#
# # Headers
# headers = {
#     "Accept": "application/json, text/plain, */*",
#     "Content-Type": "application/json",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
# }
#
# # JSON Payload
# payload = {
#     "date": "2025-02-10",
#     "from": 11320000,
#     "includeClosed": True,
#     "includePromotions": True,
#     "includeUnderDevelopment": True,
#     "loadFromDbOnUnavailability": True,
#     "to": 87330000
# }
#
# # Sending Request
# response = requests.post(url, json=payload, headers=headers)
#
# # Check response status
# if response.status_code == 200:
#     data = response.json()
# else:
#     print(f"❌ Error {response.status_code}: {response.text}")
#     exit()
#
# # Extract bus services
# buses = data.get("buses", [])
#
# # Initialize Console
# console = Console()
#
# # Create Table
# table = Table(title="Available Bus Tickets")
#
# # Define Columns
# table.add_column("#", justify="center", style="bold cyan", no_wrap=True)
# table.add_column("From", justify="center", style="green")
# table.add_column("To", justify="center", style="green")
# table.add_column("Company", justify="center", style="yellow")
# table.add_column("Departure", justify="center", style="bold magenta")
# table.add_column("Arrival", justify="center", style="bold magenta")
# table.add_column("Price", justify="center", style="bold red")
# table.add_column("Capacity", justify="center", style="blue")
# table.add_column("Bus Type", justify="center", style="cyan")
#
# # Add Rows
# for index, bus in enumerate(buses, start=1):
#     table.add_row(
#         str(index),
#         bus.get("fromName", "N/A"),
#         bus.get("toName", "N/A"),
#         bus.get("corporation", "N/A"),
#         bus.get("departureTime", "N/A"),
#         bus.get("arrivalTime", "N/A"),
#         f"{bus.get('price', 0):,} تومان",  # Format price with comma separator
#         str(bus.get("capacity", "N/A")),
#         bus.get("busType", "N/A"),
#     )
#
# # Print Table
# console.print(table)

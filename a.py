import json

# Load province and city data
with open('city.json', 'r', encoding='utf-8') as file:
    city_data = json.load(file)
    
    

cities_train = list(set(city.get('Name', 'Unknown') for city in city_data))

print(cities_train)
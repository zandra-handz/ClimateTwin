class ClimateObject:
    def __init__(self, data):
        self.name = list(data.keys())[0]
        climate_data = data[self.name]
        self.temperature = climate_data['temperature']
        self.description = climate_data['description']
        self.wind_speed = climate_data['wind_speed']
        self.wind_direction = climate_data['wind_direction']
        self.humidity = climate_data['humidity']
        self.pressure = climate_data['pressure']
        self.cloudiness = climate_data['cloudiness']
        self.sunrise_timestamp = climate_data['sunrise_timestamp']
        self.sunset_timestamp = climate_data['sunset_timestamp']
        self.latitude = climate_data['latitude']
        self.longitude = climate_data['longitude']
        self.country = climate_data['country']
        self.city_name = climate_data['city_name']


    def __str__(self):
        return f"{self.name}"
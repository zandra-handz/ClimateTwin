class ClimateObject:
    def __init__(self, data):
        self.name = list(data.keys())[0]
        climate_data = data[self.name]
        self.temperature = climate_data.get('temperature')
        self.description = climate_data.get('description')
        self.wind_speed = climate_data.get('wind_speed')
        self.wind_direction = climate_data.get('wind_direction')
        self.humidity = climate_data.get('humidity')
        self.pressure = climate_data.get('pressure')
        self.cloudiness = climate_data.get('cloudiness')
        self.sunrise_timestamp = climate_data.get('sunrise_timestamp')
        self.sunset_timestamp = climate_data.get('sunset_timestamp')
        self.latitude = climate_data.get('latitude')
        self.longitude = climate_data.get('longitude')
        self.country = climate_data.get('country')
        self.city_name = climate_data.get('city_name')
        self.state = climate_data.get('state')


    def __str__(self):
        return f"{self.name}"
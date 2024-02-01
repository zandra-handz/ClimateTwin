import math

class ClimateEncounter:
    def __init__(self, wind_direction1, wind_speed1, pressure1, humidity1, wind_direction2, wind_speed2, pressure2, humidity2):
        self.wind_direction1 = wind_direction1
        self.wind_speed1 = wind_speed1
        self.pressure1 = pressure1
        self.humidity1 = humidity1

        self.wind_direction2 = wind_direction2
        self.wind_speed2 = wind_speed2
        self.pressure2 = pressure2
        self.humidity2 = humidity2

        self.angular_difference = self.calculate_angular_difference()
        self.wind_relationship = self.categorize_wind_direction()

        self.apparent_wind_speed = self.get_apparent_wind_speed()
        self.apparent_wind_direction = self.get_apparent_wind_direction()

        self.special_relationship = False
        
        if self.wind_relationship == "Same-Heart":
            self.special_relationship = True
        else:
            self.special_relationship = False




    def calculate_angular_difference(self):
        return abs(self.wind_direction1 - self.wind_direction2) % 360

    def categorize_wind_direction(self):
        #angle = self.calculate_angular_difference() % 360

        if self.angular_difference <= 10 or self.angular_difference >= 350:
            return "Same-Heart"
        elif 170 <= self.angular_difference <= 190:
            return "Direct"
        elif 45 <= self.angular_difference <= 80 or 180 <= self.angular_difference <= 215:
            return "Perpendicular"
        elif 81 <= self.angular_difference <= 169:
            return "Slantwise"
        else:
            return "Otherside-Slatwise"


    def get_nature_of_wind_relationship_output(self):
        if self.wind_relationship == "Same-Heart":
            return "Relatively calm and steady airflow, stable weather conditions."
        elif self.wind_relationship == "Direct":
            return "Converging winds may lead to low pressure, potential for storms and heavy rainfall."
        elif self.wind_relationship == "Perpendicular":
            return "Perpendicular winds may enhance conditions for severe weather, such as thunderstorms or tornadoes."
        elif self.wind_relationship == "Slantwise":
            return "Slantwise winds could contribute to variable weather patterns with scattered precipitation."
        else:
            return "Winds at other angles may result in diverse atmospheric interactions, influencing local weather conditions in various ways."

    def get_experience_of_second_wind_output(self):
        if 0 <= self.apparent_wind_direction < 45 or 315 <= self.apparent_wind_direction <= 360:
            return "Winds are coming from the same direction as yours, maintaining current weather conditions."
        elif 45 <= self.apparent_wind_direction < 135:
            return "Wind is from the right, potentially leading to variable weather conditions."
        elif 135 <= self.apparent_wind_direction < 225:
            return "Wind here is opposite to yours, potentially causing significant changes in weather."
        elif 225 <= self.apparent_wind_direction < 315:
            return "Wind is from the left, which may result in variable weather patterns."


    def get_pressure_difference_output(self):
        pressure_difference = abs(self.pressure1 - self.pressure2)

        if pressure_difference <= 2:
            return f"Match"
        elif self.pressure1 > 1015 and self.pressure2 > 1015:
            return f"High atmospheric pressure may contribute to stable and clear weather conditions."
        elif self.pressure1 < 1005 and self.pressure2 < 1005:
            return f"Low atmospheric pressure may lead to unsettled weather with potential for precipitation."
        else:
            return f"{self.pressure1} and {self.pressure2} represent opposite atmospheric pressure conditions."


    def get_humidity_difference_output(self):
        humidity_difference = abs(self.humidity1 - self.humidity2)

        if humidity_difference <= 5:
            return f"Match"
        elif 60 <= self.humidity1 <= 80 and 60 <= self.humidity2 <= 80:
            return f"Moderate humidity levels, {self.humidity1} and {self.humidity2} may contribute to comfortable weather conditions."
        elif self.humidity1 > 80 and self.humidity2 > 80:
            return f"High humidity levels may lead to muggy and potentially rainy conditions."
        elif self.humidity1 < 60 and self.humidity2 < 60:
            return f"Low humidity levels may contribute to drier and cooler weather."
        else:
            return f"Humidity level varies from yours."


    def get_highest_wind_speed(self):
        return max(self.wind_speed1, self.wind_speed2)


    def get_apparent_wind_speed(self):
        # Calculate apparent wind speed
        theta_rad = math.radians(self.angular_difference)
        apparent_wind_speed = math.sqrt(self.wind_speed1**2 + self.wind_speed2**2 - 2 * self.wind_speed1 * self.wind_speed2 * math.cos(theta_rad))
        return apparent_wind_speed


    def get_apparent_wind_direction(self):
        # Calculate apparent wind direction
        print(self.wind_speed1)
        print(self.wind_speed2)
        cos_alpha = (self.wind_speed1**2 + self.apparent_wind_speed**2 - self.wind_speed2**2) / (2 * self.wind_speed1 * self.apparent_wind_speed)
        alpha_rad = math.acos(cos_alpha)
        alpha_deg = math.degrees(alpha_rad)

        # Determine the sign of the angle based on the relative direction of the winds
        if 0 <= self.angular_difference <= 180:
            apparent_wind_direction = (self.wind_direction1 + alpha_deg) % 360
            return apparent_wind_direction
        else:
            apparent_wind_direction = (self.wind_direction1 - alpha_deg) % 360
            return apparent_wind_direction


    def get_stronger_wind(self):
        stronger_wind = "yours" if self.wind_speed1 > self.wind_speed2 else "Second Wind"
        return stronger_wind



    def get_wind_speed_output(self):
        # Speculative interpretations based on apparent wind speed
        if self.apparent_wind_speed < 5:
            return "Wind has a mild effect on your wind, contributing to a gentle breeze."
        elif 5 <= self.apparent_wind_speed <= 15:
            return "Wind has a noticeable effect on yours, increasing resistance and creating a moderate wind."
        elif self.apparent_wind_speed > 15:
            return "The wind here has a strong impact on yours, causing significant resistance and turbulence."


    def combine_messages(self):
        humidity_output = self.get_humidity_difference_output()
        pressure_output = self.get_pressure_difference_output()
        wind_output = self.get_wind_speed_output()
        nature_of_wind_output = self.get_nature_of_wind_relationship_output()
        experience_of_second_wind_output = self.get_experience_of_second_wind_output()
        stronger_wind_output = self.get_stronger_wind()
        

        return {
            "Interaction": {
                "wind_friends": self.wind_relationship,
                "special_harmony": self.special_relationship,
                "details": nature_of_wind_output,
                "experience": experience_of_second_wind_output,
                "wind_speed_interaction": wind_output,
                "pressure_interaction": pressure_output,
                "humidity_interaction": humidity_output,
                "stronger_wind_interaction": stronger_wind_output
            }
        }


    def __str__(self):
        return f"{self.wind_relationship}"


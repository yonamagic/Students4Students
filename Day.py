
class Day:
    def __init__(self, location, date):
        self.location = location
        self.date = date
        self.available_time_ranges=['14:00-15:00', '15:15-16:15', '16:30-17:30', '17:45-18:45', '19:00-20:00', '20:15-21:15']
        self.taken_time_ranges = []

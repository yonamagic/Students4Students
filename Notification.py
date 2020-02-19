class Notification:
    def __init__(self, ID, topic, content, date, is_read):
        self.ID = ID
        self.topic = topic
        self.content = content
        self.date = date
        self.is_read = is_read
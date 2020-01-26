

class Message:

    def __init__(self, id, topic, sender, content, date, is_read):
        self.id = id
        self.topic = topic
        self.sender = sender
        self.content = content
        self.date = date
        self.is_read = is_read
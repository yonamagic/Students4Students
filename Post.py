import datetime

class Post:

    def __init__(self, post_ID, narrator, topic, content, date, comments):
        self.post_ID=post_ID
        self.narrator = narrator
        self.topic = topic
        self.content = content
        self.date = date
        self.comments = comments
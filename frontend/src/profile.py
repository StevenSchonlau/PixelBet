#https://stackoverflow.com/questions/74796781/python-json-to-object-from-model

class Profile:
    def __init__(self, username: str, id: int):
        self.username = username
        self.id = id
import requests
import json

# URL of the JSON API
url = "https://meme-api.com/gimme/Flirtymemes"

class MemeAPI:
    def __init__(self):
        self.url = url
        self.data = None

    def get_meme(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            self.data = response.json()
            print(self.data)
            return self.data
        else:
            return None
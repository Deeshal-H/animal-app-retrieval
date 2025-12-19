import requests

API_URLS = {
    "fox": "https://randomfox.ca/floof",
    "dog": "https://random.dog/woof.json",
    "duck": "https://random-d.uk/api/v2/random"
}

REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "Accept":"application/json"
}

# FUNCTION = {
#     "fox": 
# }

class AnimalAPIClient:

    def __init__(self, animal: str):
        self.url = API_URLS[animal]
    
    # def handleFox
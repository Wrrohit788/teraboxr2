import requests

class ApiKeyManager:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.current_index = 0

    def get_next_key(self):
        api_key = self.api_keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.api_keys)
        return api_key

api_keys = ["9d6f01ebc591be8658129320ae869ef178b83fe1"]
api_key_manager = ApiKeyManager(api_keys)

def post(dest, alias=None):
    api_key = api_key_manager.get_next_key()
    base_url = "runurl.in"
    payload = {
        "api": api_key,
        "url": dest
    }

    if alias:
        payload["alias"] = alias

    try:
        response = requests.get(base_url, params=payload)
        data = response.json()
        if data['status'] == "success":
            return True, data['shortenedUrl']
        else:
            return False, 'Cannot Generate Shortened URL, Contact Owner.'
    except Exception as e:
        return False, str(e)

from datetime import datetime
import requests

class Gate:
    def __init__(self, gate_id, server_url):
        self.gate = gate_id
        self.server_url = server_url

    def check_card(self, card_number, direction):
        data = {'card_number': card_number, 'gate': 1, 'timestamp': datetime.now().isoformat(), 'direction': direction}
        try:
            response = requests.post(self.server_url, json=data)
            if response.status_code == 200:
                print(f"{response.json().get('message', 'Access granted')} : {card_number}")
            else:
                print(f"{response.json().get('denied', 'Unknown error')}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending data: {e}")


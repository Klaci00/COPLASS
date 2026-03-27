from datetime import datetime
import requests
import random

class Gate:
    def __init__(self, gate_id, server_url):
        self.gate = gate_id
        self.server_url = server_url
        self.entry_connections = []
        self.exit_connections = []

    def check_card(self, card_number, direction):
        data = {'card_number': card_number, 'gate': self.gate, 'timestamp': datetime.now().isoformat(), 'direction': direction}
        try:
            response = requests.post(self.server_url, json=data)
            if response.status_code == 200:
                print(f"{response.json().get('message', 'Access granted')} : {card_number}")
                return True
            else:
                print(f"{response.json().get('denied', 'Unknown error')}: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error sending data: {e}")

class Employee:
    def __init__(self,card_number, entrance : list[Gate]):
        self.card_number = card_number
        self.direction = 0
        self.in_directions = entrance
        self.out_directions = []
    def pass_gate(self, gate : Gate):
        if gate.check_card(self.card_number, self.direction):
            print(f"Employee with card {self.card_number} passed through gate {gate.gate} in direction {"inside" if self.direction == 0 else "outside"}")
            self.out_directions = gate.exit_connections
            self.in_directions = gate.entry_connections
            if len(self.in_directions) > 0:
                self.direction = random.randint(0,1)
            else:
                self.direction = 1
    def move(self):
        self.pass_gate(random.choice(self.in_directions if self.direction == 0 else self.out_directions))

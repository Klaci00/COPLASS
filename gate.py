from datetime import datetime
import requests
import random
import logging

class Gate:
    def __init__(self, gate_id, server_url):
        self.name = None
        self.gate = gate_id
        self.server_url = server_url
        self.out_zone = None
        self.in_zone = None

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

class Zone:
    def __init__(self, in_gates : list[Gate], out_gates : list[Gate]):
        self.name = None
        self.in_gates = in_gates
        self.out_gates = out_gates

class Employee:
    def __init__(self,card_number : int, zone : Zone):
        self.name = f"Employee {card_number}"
        self.card_number = card_number
        self.zone = zone
        self.direction : int = 0
        self.logger = logging.getLogger(__name__)
    def move(self):
        if len(self.zone.in_gates) == 0:
            self.direction = 1
        elif len(self.zone.out_gates) == 0:
            self.direction = 0
        else:
            self.direction = random.randint(0,1)
        print(f'Employee has decided to go {'inside' if self.direction == 0 else 'outside'}.')

        if self.direction == 0:
            gate : Gate = random.choice(self.zone.in_gates)
        else:
            gate : Gate = random.choice(self.zone.out_gates)
            print(f'Employee has decided to go through {gate.name}.')
        if gate.check_card(self.card_number, self.direction):
            if self.zone != gate.in_zone:
                self.zone = gate.in_zone
            else:
                self.zone = gate.out_zone
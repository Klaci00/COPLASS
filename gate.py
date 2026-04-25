from datetime import datetime
from time import sleep
import requests
import random
import logging

class Gate:
    def __init__(self, gate_id, server_url):
        self.name = None
        self.gate_id = gate_id
        self.server_url = server_url
        self.current_zone = None
        self.opposite_zone = None

    def check_card(self, card_number):
        data = {'card_number': card_number, 'gate': self.gate_id, 'timestamp': datetime.now().isoformat()}
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
    def __init__(self, gates : list[Gate]):
        self.name = None
        self.gates = gates

class Employee:
    def __init__(self,card_number : int, zone : Zone):
        self.name = f"Employee {card_number}"
        self.card_number = card_number
        self.zone = zone
        
    def move(self):
        gate : Gate = random.choice(self.zone.gates)
        print(f'Employee has decided to go through {gate.name}.')
        if gate.check_card(self.card_number):
            self.zone = gate.opposite_zone
            print(f'Employee has moved to {self.zone.name}.')   
            sleep(random.uniform(1, 5))  # Simulate time taken to move through the gate
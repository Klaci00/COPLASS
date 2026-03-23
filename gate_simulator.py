import requests
import random
from datetime import datetime

SERVER_URL = 'http://127.0.0.1:8000/api/check_card_person/'

#def simulate_card_read():
    # Generate a random card ID (simulating RFID or magnetic stripe read)
 #   card_id = f"CARD-{random.randint(100000, 999999)}"
  #  return card_id

def send_card_data(card_number):
    data = {'card_number': card_number, 'gate': 1, 'timestamp': datetime.now().isoformat()}
    try:
        response = requests.post(SERVER_URL, json=data)
        if response.status_code == 200:
            print(f"{response.json().get('message', 'Access granted')} : {card_number}")
        else:
            print(f"{response.json().get('denied', 'Unknown error')}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data: {e}")

def main():
    print("Security Gate Simulator")
    print("Press Enter to simulate a person passing through the gate...")
    
    while True:
        input("Press Enter to simulate...")
        card_number = int(input("Enter card number"))
        print(f"Read card: {card_number}")
        send_card_data(card_number)

if __name__ == '__main__':
    main()
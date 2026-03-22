import requests
import random
import time

SERVER_URL = 'http://localhost:5000/card_data'

def simulate_card_read():
    # Generate a random card ID (simulating RFID or magnetic stripe read)
    card_id = f"CARD-{random.randint(100000, 999999)}"
    return card_id

def send_card_data(card_id):
    data = {'card_id': card_id}
    try:
        response = requests.post(SERVER_URL, json=data)
        if response.status_code == 200:
            print(f"Successfully sent card data: {card_id}")
        else:
            print(f"Failed to send card data: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data: {e}")

def main():
    print("Security Gate Simulator")
    print("Press Enter to simulate a person passing through the gate...")
    
    while True:
        input("Press Enter to simulate...")
        card_id = simulate_card_read()
        print(f"Read card: {card_id}")
        send_card_data(card_id)

if __name__ == '__main__':
    main()
import random
from gate import Gate

SERVER_URL = 'http://127.0.0.1:8000/api/check_card_person/'

def main():
    print("Security Gate Simulator")
    print("Press Enter to simulate a person passing through the gate...")
    g1 = Gate(gate_id=1, server_url=SERVER_URL)
    while True:
        input("Press Enter to simulate...")
        card_number = int(input("Enter card number"))
        print(f"Read card: {card_number}")
        g1.check_card(card_number=card_number, direction=random.randint(0,1))

if __name__ == '__main__':
    main()
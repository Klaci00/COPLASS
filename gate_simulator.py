import random
from gate import Gate

SERVER_URL = 'http://127.0.0.1:8000/api/check_card_person/'

def main():
    print("Security Gate Simulator")
    print("Press Enter to simulate a person passing through the gate...")
    g1 = Gate(gate_id=1, server_url=SERVER_URL)
    g2 = Gate(gate_id=2, server_url=SERVER_URL)
    while True:
        input("Press Enter to simulate...")
        card_number = int(input("Enter card number"))
        direction = int(input("Enter direction (0 for outside to inside, 1 for inside to outside)"))
        print(f"Read card: {card_number}")
        g2.check_card(card_number=card_number, direction=direction)

if __name__ == '__main__':
    main()
import time
from gate import Gate, Employee

SERVER_URL = 'http://127.0.0.1:8000/api/check_card_person/'

def main():
    print("Security Gate Simulator")
    print("Press Enter to simulate a person passing through the gate...")
    g1 = Gate(gate_id=1, server_url=SERVER_URL)
    g2 = Gate(gate_id=2, server_url=SERVER_URL)
    e1 = Employee(card_number=32, entrance=[g1])
    g1.entry_connections = [g2]
    g1.exit_connections = [g1]
    g2.exit_connections = [g2,g1]

    while True:
        e1.move()
        time.sleep(5)

if __name__ == '__main__':
    main()
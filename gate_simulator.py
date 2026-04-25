import time
from gate import Gate, Employee, Zone
from threading import Thread

SERVER_URL = 'http://127.0.0.1:8000/api/check_card_person/'

def main():
    print("Security Gate Simulator")
    print("Press Enter to simulate a person passing through the gate...")
    from_out_to_lobby = Gate(gate_id=1, server_url=SERVER_URL)
    from_out_to_lobby.name = 'from_out_to_lobby'
    from_lobby_to_out = Gate(gate_id=2, server_url=SERVER_URL)
    from_lobby_to_out.name = 'from_lobby_to_out'
    from_lobby_to_secret = Gate(gate_id=3, server_url=SERVER_URL)
    from_lobby_to_secret.name = 'from_lobby_to_secret'
    from_secret_to_lobby = Gate(gate_id=4, server_url=SERVER_URL)
    from_secret_to_lobby.name = 'from_secret_to_lobby'
    outside = Zone(gates=[from_out_to_lobby])
    outside.name = 'outside'
    lobby = Zone(gates=[from_lobby_to_out, from_lobby_to_secret])
    lobby.name = 'lobby'
    secret = Zone(gates=[from_secret_to_lobby])
    secret.name = 'secret'
    from_out_to_lobby.current_zone = outside
    from_out_to_lobby.opposite_zone = lobby
    from_lobby_to_out.current_zone = lobby
    from_lobby_to_out.opposite_zone = outside
    from_lobby_to_secret.current_zone = lobby
    from_lobby_to_secret.opposite_zone = secret
    from_secret_to_lobby.current_zone = secret
    from_secret_to_lobby.opposite_zone = lobby
    employees = []
    for i in range(1,101):
        e = Employee(card_number=int(f'{i}1'), zone=outside)
        employees.append(e)
    '''        
    e1 = Employee(11, outside)
    e1.zone = outside
    '''
    def simulate_employee_movement(employee):
        while True:
            employee.move()
    for e in employees:
        Thread(target=simulate_employee_movement, args=(e,)).start()          

if __name__ == '__main__':
    main()
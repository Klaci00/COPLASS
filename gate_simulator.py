import time
from gate import Gate, Employee, Zone
import logging

SERVER_URL = 'http://127.0.0.1:8000/api/check_card_person/'

def main():
    logger = logging.getLogger(__name__)
    print("Security Gate Simulator")
    print("Press Enter to simulate a person passing through the gate...")
    from_out_to_asd = Gate(gate_id=1, server_url=SERVER_URL)
    from_out_to_asd.name = 'from_out_to_asd'
    from_asd_to_csil = Gate(gate_id=2, server_url=SERVER_URL)
    from_asd_to_csil.name = 'from_asd_to_csil'
    from_csil_to_out = Gate(gate_id=3, server_url=SERVER_URL)
    from_csil_to_out.name = 'from_csil_to_out'
    out = Zone(in_gates=[from_out_to_asd], out_gates=[])
    out.name = 'out'
    asd = Zone(in_gates=[from_asd_to_csil], out_gates=[from_out_to_asd])
    asd.name = 'asd'
    csil = Zone(in_gates=[], out_gates=[from_csil_to_out])
    csil.name = 'csil'
    from_out_to_asd.in_zone = asd
    from_out_to_asd.out_zone = out
    from_asd_to_csil.in_zone = csil
    from_asd_to_csil.out_zone = asd
    from_csil_to_out.in_zone = csil
    from_csil_to_out.out_zone = out
    e1 = Employee(11, out)
    e1.zone = out
    while True:
        print(f'Employee is in {e1.zone.name}.')
        e1.move()
        time.sleep(5)

if __name__ == '__main__':
    main()
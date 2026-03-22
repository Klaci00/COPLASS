# Security Gate Simulator
# This project simulates a security gate system where card data is read and sent to a server.

## Components
- `server.py`: A Flask server that receives card data via POST requests.
- `gate_simulator.py`: Simulates the security gate by generating card IDs and sending them to the server.
- `requirements.txt`: Lists the required Python packages.

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `python server.py`
3. In another terminal, run the simulator: `python gate_simulator.py`

## Usage
- The simulator will wait for user input to simulate a person passing through.
- Each simulation generates a random card ID and sends it to the server.
- The server logs the received card data.
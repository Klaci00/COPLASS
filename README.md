# COPLASS - Complex Plant Security Solutions 

A full-stack application that handles a security gate system with card-based access control, site access control, vehicle access control, employee data control, randomised checks, work permits, health evaluation documentation for employees and many more functions in the future. It includes a Django REST API backend for validating entries, a Vue.js frontend for user interactions, and Python scripts for simulating gate operations.

## Features

- **Backend API**: Django REST framework for handling card validation and employee data.
- **Frontend Interface**: Vue.js application with views for login, dashboard, access requests, and messages.
- **Gate Simulator**: Python scripts to simulate card reading and sending data to the server.
- **Database**: SQLite for storing employee and access data.

## Components

- `django-rest-server/`: Django project containing the REST API.
  - `entry_validation/`: Main Django app with models, views, and URLs.
  - `card_person_check/`: App for card and person validation logic.
- `frontend/requests-front/`: Vue.js frontend built with Vite.
- `gate_simulator.py`: Script to simulate gate operations.
- `gate.py`: Supporting module for gate logic.
- `requirements.txt`: Python dependencies.

## Prerequisites

- Python 3.8+
- Node.js 16+
- pip
- npm or yarn

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Klaci00/COPLASS.git
   cd COPLASS
   ```

2. Set up the backend:
   ```
   cd django-rest-server
   pip install -r ../requirements.txt
   python manage.py migrate
   ```

3. Set up the frontend:
   ```
   cd ../frontend/requests-front
   npm install
   ```

## Running the Application

1. Start the Django backend:
   ```
   cd django-rest-server
   python manage.py runserver
   ```
   The API will be available at http://localhost:8000

2. Start the frontend:
   ```
   cd ../frontend/requests-front
   npm run dev
   ```
   The frontend will be available at http://localhost:5173

3. (Optional) Run the gate simulator:
   ```
   python gate_simulator.py
   ```

## Usage

- Use the frontend to log in, view dashboard, request access rights, and check messages.
- The gate simulator generates card IDs and sends them to the backend for validation.
- The backend API validates cards against the database and returns access decisions.

## API Endpoints

- `POST /api/check/`: Validate a card ID and return access information.

## Contributing

Please follow standard Git practices. Create a branch for new features and submit pull requests.

## License

[Add license if applicable]

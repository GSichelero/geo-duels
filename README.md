# GeoDuels

## Setting up your local environment
- clone the repository

### Backend
- in the backend folder, create a virtual environment with: python3 -m venv venv
- activate the virtual environment: source venv/bin/activate (MacOS), .\venv\Scripts\activate (Windows)
- then install the python packages: pip install -r requirements.txt
- if necessary, create migration with the database changes recently made: python manage.py makemigrations
  - migrate to the PostgreSQL database: python manage.py migrate
- run the server: python manage.py runserver

### Frontend
- in the frontend/client folder, run: npm install
- in the frontend/client folder, run: npm run build
- in the frontend folder, run: npm install
- in the frontend folder, run: npm start
- in the browser navigate to (Production): http://localhost:5000
- optionally you can also navigate into frontend/client, then run: npm start
  - then from there in the browser navigate to (Development): http://localhost:3000

# GeoDuels :earth_americas:

### Gameplay
- Cada jogador escolhe um número predeterminado de localizações no mapa do mundo (Google Maps API).
- Após as localizações serem escolhidas, cada jogador vai poder ter uma visão do Google Street View de cada localização que o jogador adversário escolheu.
- O jogador então terá que tentar adivinhar a localização de cada visão do Google Street View que o adversário escolheu e marcar sua escolha no mapa.
- Após os 2 jogadores fazerem todas as suas escolhas, é calculada a distância do ponto do mapa que o jogador escolheu até a localização real.
- O jogador que tiver na soma final a menor distância vence.

### Tecnologias:
- Frontend: Javascript
- Backend: Python
- Framework WEB: React
- Framework Backend: Django
- Banco de Dados: PostgreSQL, MongoDB
- Comunicação: REST API e WebSockets
- Visualização do mapa e das localizações: Google Maps e Google Street View APIs.

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

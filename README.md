
# Starting Project


## VENV

- `cd <repo>`
- `python -m venv .venv` to create your new environment (called 'venv' here)
- `source .venv/bin/activate` to enter the virtual environment
- `pip install -r requirements.txt` to install the requirements in the current environment

Make sure your uvicorn process is still running before you continue. If it's not, you can start with the same command in the terminal:

`python -m uvicorn main:app --reload`
Navigate to the http://localhost:8000/docs URL in your browser. This is the API documentation page that FastAPI and Swagger generated for us!

## Build Docker image
https://www.youtube.com/watch?v=zkMRWDQV4Tg&list=PLC0nd42SBTaO3aajVi2FomC86q6TeRM_Y
`docker build -t raincheck .`

## Run Docker image
`docker run -d -p 8080:80 raincheck`

Navigate to the http://localhost:8080/docs URL in your browser. This is the API documentation page that FastAPI and Swagger generated for us!

## Docker Compose Up
`docker compose up --build --detach` First time
`docker compose up --detach` Successive times.
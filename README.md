
# Starting Project


## Build Docker image
https://www.youtube.com/watch?v=zkMRWDQV4Tg&list=PLC0nd42SBTaO3aajVi2FomC86q6TeRM_Y
`docker build -t raincheck .`

## Run Docker image
`docker run -d -p 8080:80 raincheck`

Navigate to the http://localhost:8080/docs URL in your browser. This is the API documentation page that FastAPI and Swagger generated for us!

## Docker Compose Up
`docker compose up --build --detach` First time
`docker compose up --detach` Successive times.
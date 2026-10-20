# Exercise 04: Docker Networking with Multiple Containers

## Objective
Understand Docker bridge networking and run a Flask REST API, MySQL database, and Redis cache on a shared user-defined Docker network.

## Technologies Used
- Docker and Docker Desktop
- Python 3.9
- Flask
- MySQL
- Redis
- PowerShell

## Project Structure

```text
Exercise-04-Docker-Networking/
├── app.py
├── requirements.txt
├── Dockerfile
├── README.md
└── evidence/
    ├── api-response.json
    ├── containers.txt
    └── network-inspect.json
```

## Implementation

### 1. Create the Docker network

```powershell
docker network create --driver bridge my-bridge-net
docker network ls
docker network inspect my-bridge-net
```

### 2. Build the Flask image

```powershell
docker build -t flask-api .
```

### 3. Start the containers

```powershell
docker run -d --name mysql --network my-bridge-net -e MYSQL_ROOT_PASSWORD=<LOCAL_PASSWORD> mysql:latest
docker run -d --name redis --network my-bridge-net redis:latest
docker run -d --name flask --network my-bridge-net -p 5001:5001 flask-api
```

Replace `<LOCAL_PASSWORD>` with a local practice password. Do not commit real credentials.

### 4. Test the REST API

Endpoint: `GET http://localhost:5001/about`

Expected JSON response:

```json
{
  "name": "Simple REST API",
  "version": "1.0",
  "description": "This is a simple REST API built with Flask."
}
```

### 5. Verify container-name resolution

```powershell
docker exec flask python -c "import socket; print('MySQL:', socket.gethostbyname('mysql')); print('Redis:', socket.gethostbyname('redis'))"
```

Both container names resolved successfully to IP addresses on `my-bridge-net`.

## Results

- Created the user-defined bridge network `my-bridge-net`.
- Started Flask, MySQL, and Redis containers on the same network.
- Published Flask port 5001 to the host.
- Successfully tested the `/about` endpoint.
- Verified that Flask could resolve the MySQL and Redis container names.
- Saved API output, container status, and network inspection under `evidence/`.

**Note:** The Flask API demonstrates the network setup and DNS resolution. It does not currently execute database queries against MySQL or cache operations against Redis.

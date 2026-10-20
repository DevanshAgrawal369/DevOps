# Exercise 2: Deploy a Flask App on Minikube

## Objective

Deploy a Python Flask web application on a local Kubernetes cluster using Minikube, Docker, kubectl, and YAML configuration files.

## Technologies Used

- Python and Flask
- Docker
- Kubernetes
- Minikube
- kubectl
- Git and GitHub

## Application

The Flask application listens on port `15000` and responds to requests at `/` with:

```text
Hello from Flask on Kubernetes!
```

## Project Structure

```text
flask-minikube-exercise/
├── app.py
├── Dockerfile
├── .dockerignore
├── README.md
├── k8s/
│   └── flask-deployment.yaml
└── evidence/
    ├── verification.txt
    └── flask-page.png
```

## Build and Load the Docker Image

```powershell
docker build -t flask-app:latest .
minikube image load flask-app:latest
```

## Deploy to Kubernetes

```powershell
kubectl apply -f k8s/flask-deployment.yaml
kubectl rollout status deployment/flask-app
```

## Verify the Deployment

```powershell
kubectl get deployments
kubectl get pods -l app=flask-app
kubectl get services flask-app-service
kubectl logs deployment/flask-app
```

## Access the Application

```powershell
minikube service flask-app-service --url
```

Keep the terminal running while testing the returned URL.

## Cleanup

```powershell
kubectl delete -f k8s/flask-deployment.yaml
minikube stop
```

## Learning Outcomes

- Built a Docker image for a Flask application.
- Loaded a local image into Minikube.
- Deployed an application using a Kubernetes Deployment.
- Exposed the application using a NodePort Service.
- Verified application status and logs.
- Prepared deployment files and evidence for GitHub.

## Current evidence

The running Flask Deployment and Service were rechecked on 2026-10-20. A temporary port-forward returned the expected body with HTTP 200. See [`evidence/screenshot-checklist.md`](evidence/screenshot-checklist.md) and [the live capture](evidence/screenshots/01-flask-live.png).

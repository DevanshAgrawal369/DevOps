# Kubernetes Hands-On Exercise 1: Hello Pod

## Overview

This project demonstrates how to deploy and access a containerized web application using Kubernetes and Minikube.

I deployed an Nginx container inside a Kubernetes Pod and exposed it using a NodePort Service.

## Objectives

- Set up a local Kubernetes cluster using Minikube.
- Deploy an Nginx Pod.
- Expose the Pod using a Kubernetes Service.
- Access the Nginx welcome page in a browser.
- Store configuration files and deployment evidence in GitHub.

## Technologies Used

- Kubernetes
- Minikube
- Docker Desktop
- kubectl
- Nginx
- Git and GitHub

## Project Structure

```text
kubernetes-hands-on/
├── README.md
├── k8s/
│   ├── pod.yaml
│   └── service.yaml
└── evidence/
    ├── verification.txt
    └── nginx-page.png
```

## Prerequisites

Install Docker Desktop, Minikube, kubectl, and Git.

Ensure Docker Desktop is running before starting Minikube.

## Deployment Steps

### 1. Start the Kubernetes cluster

```bash
minikube start --driver=docker
```

### 2. Deploy the Kubernetes resources

```bash
kubectl apply -f k8s/
```

### 3. Verify the Pod and Service

```bash
kubectl get nodes
kubectl get pods
kubectl get services
kubectl get endpoints hello-k8s
```

### 4. Access the application

```bash
minikube service hello-k8s
```

The browser should display the default Nginx welcome page.

## Configuration Files

- `k8s/pod.yaml`: Defines the Nginx Pod and its container.
- `k8s/service.yaml`: Exposes the Pod through a NodePort Service.

## Evidence

The `evidence/` directory contains deployment verification output and a screenshot of the Nginx welcome page.

## Cleanup

```bash
kubectl delete -f k8s/
minikube stop
```

## Learning Outcomes

- Learned how to create and manage Kubernetes Pods.
- Understood how Kubernetes Services route traffic to Pods.
- Practiced deploying resources using YAML manifests.
- Verified application availability using kubectl and Minikube.
- Used Git to prepare a project for GitHub.
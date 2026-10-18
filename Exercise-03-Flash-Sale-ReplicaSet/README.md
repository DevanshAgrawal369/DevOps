# Exercise 3: Scaling a Flash Sale App Using Kubernetes ReplicaSets

## Objective
Understand ReplicaSets and Pods, scale a Flask application, observe Pod placement, and verify Kubernetes self-healing.

## Real-World Use Case
During an e-commerce flash sale, a sudden increase in traffic can require multiple instances of an application. Kubernetes ReplicaSets maintain the configured number of Pod replicas.

## Technologies
- Python and Flask
- Gunicorn
- Docker
- Kubernetes
- Minikube
- kubectl

## Application Endpoints
- `/` — Displays the Big Sale welcome message and serving Pod hostname.
- `/buy?user=123` — Simulates a purchase and reports the product, user, and serving Pod.
- `/health` — Returns application health information.

## Deployment
The `k8s/flashsale-replicaset.yaml` file defines:
- ReplicaSet `flashsale-rs`
- Initial replica count of 3
- Service `flashsale-svc`
- Readiness and liveness probes
- Container resource requests and limits

## Scaling and Self-Healing
1. Deployed the ReplicaSet with 3 Pods.
2. Scaled the ReplicaSet to 5 Pods.
3. Deleted one Pod manually.
4. Verified that Kubernetes created a replacement.
5. Confirmed that all 5 Pods were Ready on the single Minikube node.

## Verification Commands
```powershell
kubectl get rs flashsale-rs
kubectl get pods -o wide -l app=flashsale
kubectl get services flashsale-svc
kubectl describe rs flashsale-rs
```

## Access the Application
Start port forwarding:
```powershell
kubectl port-forward service/flashsale-svc 8080:80
```

Test the endpoints at `http://127.0.0.1:8080/`, `/buy?user=123`, and `/health`.

## Learning Outcomes
- Understood ReplicaSet desired state.
- Scaled an application from 3 to 5 Pods.
- Observed Pod IP addresses and single-node placement.
- Verified automatic Pod replacement after deletion.
- Tested the application through a Kubernetes Service.

Note: Multiple replicas demonstrate replication and recovery; this exercise does not benchmark flash-sale traffic capacity.

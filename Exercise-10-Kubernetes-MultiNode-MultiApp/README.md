# Exercise 10 — Multi-Node Kubernetes Cluster with Multiple Applications

## Objective and current status

Deploy two small Flask services to Kubernetes: Product Catalog with two replicas and Shopping Cart with three. Required pod anti-affinity uses `kubernetes.io/hostname` so each service replica lands on a different node. The exercise also tests Service endpoints, live HTTP behavior, and Deployment self-healing.

**Current status: local source and manifests are prepared; remote cluster verification is pending.** The existing Windows Minikube profile is preserved. No three-node local profile was started because available host memory is limited. No Killercoda session was available to this agent, so the actual remote node count, image pulls, deployment, endpoints, replica placement, live HTTP tests, and self-healing have not been verified. The public playground page requires JavaScript and was inaccessible in the available browser surface. The official Killercoda Creator documentation lists one-node and two-node kubeadm environment templates; it does not establish the node count of the standard playground. Verify the actual session before applying manifests. [Killercoda playground](https://killercoda.com/playgrounds/scenario/kubernetes) · [Killercoda environment documentation](https://killercoda.com/creators)

Local validation was run in a temporary isolated Python virtual environment: all 8 unit tests passed (2 Catalog, 6 Cart), and all five Kubernetes YAML documents parsed with the expected replicas and required anti-affinity. Both Docker images built and loopback smoke tests passed, including health checks, non-root runtime identity, catalog JSON, and Cart POST followed by GET. These are local unit and Docker checks, not Kubernetes results. See [`evidence/verification.txt`](evidence/verification.txt) for measured results. The remote cluster remains pending.

## Architecture

```text
                       Kubernetes namespace: devops-exercise-10
       ┌─────────────────────────────┐      ┌─────────────────────────────┐
       │ Product Catalog Service    │      │ Shopping Cart Service       │
       │ ClusterIP :80 → pod :8080   │      │ ClusterIP :80 → pod :8080   │
       └──────────────┬──────────────┘      └──────────────┬──────────────┘
                      │                                    │
              2 Catalog pods                       3 Cart pods
           required distinct-hosts              required distinct-hosts
                      └──────────── three schedulable nodes ─────────────┘
```

The deployments use required anti-affinity scoped to their own app labels. Product Catalog needs two schedulable nodes; Shopping Cart needs three. A cluster with fewer than three schedulable nodes cannot satisfy the Cart rule, so some replicas will remain Pending. The manifests tolerate the standard control-plane `NoSchedule` taint for small lab clusters; this is a learning convenience, not a production recommendation.

## Project structure

```text
Exercise-10-Kubernetes-MultiNode-MultiApp/
├── app-a-product-catalog/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/test_app.py
├── app-b-shopping-cart/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/test_app.py
├── k8s/
│   ├── namespace.yaml
│   ├── product-catalog-deployment.yaml
│   ├── product-catalog-service.yaml
│   ├── shopping-cart-deployment.yaml
│   └── shopping-cart-service.yaml
├── scripts/
│   ├── verify-local.ps1
│   ├── verify-cluster.sh
│   └── test-endpoints.sh
├── requirements-dev.txt
├── evidence/
│   ├── remote-execution-guide.md
│   ├── screenshot-checklist.md
│   ├── verification.txt
│   └── screenshots/
└── README.md
```

## Applications and APIs

Both containers run Python 3.12, pinned Flask/Werkzeug/Gunicorn dependencies, and a one-worker Gunicorn server as UID 10001. They listen on container port 8080 and do not enable Flask debug mode. Kubernetes Services expose port 80 and route to named target port 8080. Pods drop Linux capabilities, disallow privilege escalation, use the default seccomp profile, and use a read-only root filesystem with a temporary `/tmp` volume.

### Product Catalog (App A)

- `GET /products` returns `{"products":[...]}` for Laptop ($1200), Phone ($800), and Headphones ($150).
- `GET /health` returns `{"status":"ok"}` for probes.

### Shopping Cart (App B)

- `GET /cart` returns `{"items":[]}` in a fresh process.
- `POST /cart` accepts `product_id`, `name`, `price`, and positive integer `quantity`; valid items return HTTP 201.
- Non-JSON media types return HTTP 415. Invalid JSON and invalid fields return HTTP 400 with an error message.
- `GET /health` returns `{"status":"ok"}`.

The cart is an in-memory Python list. Each pod has its own copy, and a pod restart clears that copy. The Service can route consecutive requests to different replicas, so the deterministic POST/GET demonstration uses a `kubectl port-forward` directly to one pod. This is not shared or durable cart storage.

## Prerequisites

For local preparation: Git, Python 3.10+, Docker Desktop's Linux engine, and PyYAML for local manifest parsing. For remote deployment: a Kubernetes cluster with at least three Ready, schedulable nodes; `kubectl`, `git`, `curl`, and Python 3 on the remote terminal; and a way for all nodes to pull the same image tags.

The current local Minikube profile is named `minikube`, uses Kubernetes v1.37.0 and has one Ready node with existing applications. It must not be changed for this exercise. Remote commands run inside the remote playground terminal; they do not use this local kubeconfig.

## Prepare and test locally

From Windows PowerShell at the repository root:

```powershell
Set-Location C:\Users\devan\DevOps\Exercise-10-Kubernetes-MultiNode-MultiApp
.\scripts\verify-local.ps1
```

The local script creates a temporary virtual environment, installs the pinned application and development dependencies, runs each application's `unittest` suite, and parses every Kubernetes YAML document with PyYAML. It checks replica counts and required hostname anti-affinity, then removes the temporary environment. It does not contact or modify any Kubernetes cluster.

Build the local test images:

```powershell
docker build -f app-a-product-catalog\Dockerfile -t product-catalog:exercise10 app-a-product-catalog
docker build -f app-b-shopping-cart\Dockerfile -t shopping-cart:exercise10 app-b-shopping-cart
```

The `evidence/remote-execution-guide.md` contains optional, loopback-only Docker smoke commands and the remote image-publishing steps. No image has been published to a registry as part of local preparation.

## Remote playground: inspect before deployment

1. Open the official [Killercoda Kubernetes playground](https://killercoda.com/playgrounds/scenario/kubernetes) and start a session.
2. In its Linux terminal run `kubectl config current-context`, `kubectl get nodes -o wide`, and the capacity/taint inspection command in the remote guide.
3. Continue only if at least three nodes are Ready and schedulable. The current playground node count is not verified. Do not run these commands against the local Minikube context.
4. Clone this public repository's Exercise 10 folder in the remote session, publish or import the images using the guide, and apply the namespace and manifests.

The remote guide contains the complete numbered sequence for deployment, endpoint tests, self-healing, evidence capture, and safe namespace cleanup. Public GHCR packages are one possible distribution fallback. Anyone can pull a public package, so publish only the sample application and make package visibility Public only after inspecting it. Never place a registry token in Git or chat. Do not use GHCR unless the selected playground cannot safely build and distribute the image itself.

## Kubernetes configuration

- Namespace: `devops-exercise-10`.
- Deployments: `product-catalog` (2 replicas) and `shopping-cart` (3 replicas).
- Services: `product-catalog-service` and `shopping-cart-service`, both ClusterIP on port 80.
- Readiness and liveness: HTTP GET `/health`.
- Requests: 50m CPU / 64Mi memory per pod. Limits: 250m / 128Mi.
- Required anti-affinity: each Deployment excludes its own app label from the same `kubernetes.io/hostname`.
- Local manifest image tags: `product-catalog:exercise10`, `shopping-cart:exercise10`, `IfNotPresent`. Remote instructions replace these with the chosen public image references before applying.

The Cart Deployment uses `maxSurge: 0` and `maxUnavailable: 1` so an update does not ask required anti-affinity to schedule a fourth temporary Cart pod on only three hosts.

## Verify remote deployment

Run `./scripts/verify-cluster.sh` in the remote Linux session. It fails nonzero if fewer than three Ready schedulable nodes exist, replica counts do not match, pods are not Running and Ready, replicas are not on distinct nodes, or a Service has no ready endpoint. Inspect `kubectl get pods -o wide`, Deployments, Services, and Endpoints in addition to the script output.

Run `./scripts/test-endpoints.sh` to test the actual Kubernetes Services. It checks the exact catalog JSON, a valid Cart Service response, and a POST followed by GET on one selected Cart pod. The script uses temporary port-forward processes and cleans up only the processes it started. See the remote guide for a manual equivalent and for changing ports if one is occupied.

## Self-healing demonstration

After capturing the initial healthy state, delete one pod at a time using the app-specific label selector in the remote guide. Wait for the relevant Deployment rollout to complete, record the old and replacement pod names and nodes, and rerun `verify-cluster.sh`. A pass requires all five pods to return Ready with their required distinct-node placement. Never delete a node or another exercise's workload.

## Local verification and remote status

**Prepared locally:** independent Flask applications, input validation, unit tests, pinned runtime dependencies, non-root Dockerfiles, Kubernetes manifests, local verifier, live-cluster verifier, and endpoint/self-healing instructions.

**Pending remote observation:** Killercoda node count/capacity, image distribution, Deployment/Service rollout, actual endpoint responses, three-node placement, self-healing, and remote screenshots. The checklist marks all 14 required screenshots pending until genuine images are captured and visually inspected. Local unit tests or Docker smoke checks cannot substitute for remote Kubernetes evidence.

## Troubleshooting

- **Shopping Cart pods Pending:** verify at least three Ready schedulable hostnames and inspect `kubectl describe pod`; required anti-affinity is intentional and must not be weakened.
- **ImagePullBackOff:** verify the exact immutable tag, public package visibility or private pull configuration, and remote-node network access. Local Docker images are not automatically visible to remote containerd nodes.
- **Readiness/liveness failures:** inspect pod logs and events; confirm the server binds to `0.0.0.0:8080` and probes target `/health` on the named port.
- **No Service endpoints:** compare Service selectors with pod labels and check readiness.
- **Cannot access ClusterIP externally:** use the supplied `kubectl port-forward` tests from the remote terminal; do not guess a NodePort or expose credentials.
- **Port-forward conflict:** choose free remote-local ports using the script's environment variables; it does not terminate an existing listener.
- **Cart item not present through Service:** another replica may have received the request. Repeat POST and GET through one pod port-forward; state is deliberately not shared.
- **Playground expires:** save command outputs and screenshots before closing the session. Killercoda sessions are temporary; do not use them for secrets or durable data.

## Evidence index

- [`evidence/verification.txt`](evidence/verification.txt): actual preflight and verification results, including pending remote checks.
- [`evidence/remote-execution-guide.md`](evidence/remote-execution-guide.md): numbered Windows/remote-terminal procedure.
- [`evidence/screenshot-checklist.md`](evidence/screenshot-checklist.md): capture, open, visual-inspection, and completion states for every required image.

## Cleanup

Remote cleanup is limited to `kubectl delete namespace devops-exercise-10` inside the remote cluster after saving evidence. This does not run against the local Windows Minikube profile. Do not run `minikube delete` or stop/reconfigure existing local services for this exercise.

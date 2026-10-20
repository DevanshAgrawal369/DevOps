# Remote execution guide — Exercise 10

This guide uses the public Killercoda Kubernetes playground. A remote browser session is not connected to the local Windows `kubectl` context. Run the Linux commands below only in the terminal displayed by the Killercoda browser.

## Before you start

Open [Killercoda's Kubernetes playground](https://killercoda.com/playgrounds/scenario/kubernetes) in your browser and start its standard playground. The page is JavaScript-driven; no session has been started by this project. Killercoda documents one-node and two-node kubeadm environment templates and temporary sessions. The actual playground node count must be checked in the session. This exercise requires **three Ready, schedulable nodes** because Cart has three replicas and required hostname anti-affinity. If that check fails, stop here; do not remove anti-affinity or claim a multi-node result.

Killercoda says its free scenarios are temporary (normally up to one hour) and that public traffic URLs are not password-protected. Do not put secrets or private data in the session. Save command output and screenshots before closing it. See [Killercoda Creator documentation](https://killercoda.com/creators) for environment and lifetime details.

The built application images are not published yet. The manifests use local tags for local Docker testing. For remote execution, publish the two images to a registry first, then substitute their immutable tag in copied manifests as shown below. A public GHCR image is anonymously downloadable by anyone and may be cached by third parties; publish only these sample applications, never credentials or private data. Do not enter a token in this repository, a manifest, or chat. If you do not want the images public, stop and use an authenticated private registry that your selected nodes can access.

## 1. Confirm the remote cluster

In the Killercoda Linux terminal:

```bash
date -Is
kubectl config current-context
kubectl get nodes -o wide
kubectl get nodes -o json | python3 -c 'import json,sys; d=json.load(sys.stdin); [print(n["metadata"]["name"], "ready="+str(next((c["status"] for c in n["status"]["conditions"] if c["type"]=="Ready"),"Unknown")), "unschedulable="+str(n["spec"].get("unschedulable",False)), "cpu="+n["status"]["allocatable"].get("cpu","?"), "memory="+n["status"]["allocatable"].get("memory","?"), "taints="+str(n["spec"].get("taints",[]))) for n in d["items"]]'
kubectl describe nodes
```

Count at least three nodes with `Ready=True` and `spec.unschedulable` absent/false. Ensure each has enough allocatable CPU and memory for at least one pod request (50m CPU and 64Mi memory). The manifests tolerate the standard control-plane `NoSchedule` taint to allow a small lab cluster to use that node; production clusters should use dedicated workers. If fewer than three usable nodes exist, do not apply the Deployments. Open a different legitimate three-node cluster and repeat these checks.

## 2. Obtain this exercise's files

After the Exercise 10 folder is committed and pushed to the public DevOps repository, use the remote Linux terminal:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/DevanshAgrawal369/DevOps.git /tmp/devops-ex10
cd /tmp/devops-ex10
git sparse-checkout set Exercise-10-Kubernetes-MultiNode-MultiApp
cd Exercise-10-Kubernetes-MultiNode-MultiApp
find . -maxdepth 3 -type f -print
```

This is a clone in the remote session only. It does not use or alter the Windows kubeconfig. If the playground lacks Git, stop and use its documented file upload/IDE facility; do not paste secrets into the terminal.

## 3. Build and publish images (Windows PowerShell)

Run this in a separate **local PowerShell** terminal after the files have been pushed. Publishing to GHCR is optional until the remote session's build/image-import capabilities are known. Public packages make these images visible and pullable by anyone. The image source is already public sample code, but verify the Docker build context contains no private files before pushing.

```powershell
Set-Location C:\Users\devan\DevOps
$Tag = "ex10-$(git rev-parse --short HEAD)"
$CatalogImage = "ghcr.io/devanshagrawal369/devops-ex10-product-catalog:$Tag"
$CartImage = "ghcr.io/devanshagrawal369/devops-ex10-shopping-cart:$Tag"
docker build -f Exercise-10-Kubernetes-MultiNode-MultiApp\app-a-product-catalog\Dockerfile -t $CatalogImage Exercise-10-Kubernetes-MultiNode-MultiApp\app-a-product-catalog
docker build -f Exercise-10-Kubernetes-MultiNode-MultiApp\app-b-shopping-cart\Dockerfile -t $CartImage Exercise-10-Kubernetes-MultiNode-MultiApp\app-b-shopping-cart
docker login ghcr.io --username DevanshAgrawal369
docker push $CatalogImage
docker push $CartImage
```

`docker login` prompts locally. Never place a PAT in a command, file, screenshot, or chat. If authentication asks for a token and you do not already have a suitable credential, stop and configure registry access locally. In GitHub, set each package's visibility to Public only after confirming the package contains just this exercise's sample app. Record the exact `$Tag`. Do not use `latest` for the demonstration.

## 4. Apply manifests with the published image tag

Back in the **Killercoda Linux terminal**, set the tag printed by PowerShell. Replace `ex10-<short-commit>` with its actual value:

```bash
export IMAGE_TAG='ex10-<short-commit>'
export CATALOG_IMAGE="ghcr.io/devanshagrawal369/devops-exercise10-product-catalog:${IMAGE_TAG}"
export CART_IMAGE="ghcr.io/devanshagrawal369/devops-exercise10-shopping-cart:${IMAGE_TAG}"
sed "s|product-catalog:exercise10|${CATALOG_IMAGE}|g" k8s/product-catalog-deployment.yaml > /tmp/product-catalog-deployment.yaml
sed "s|shopping-cart:exercise10|${CART_IMAGE}|g" k8s/shopping-cart-deployment.yaml > /tmp/shopping-cart-deployment.yaml
kubectl apply -f k8s/namespace.yaml
kubectl apply -f /tmp/product-catalog-deployment.yaml
kubectl apply -f k8s/product-catalog-service.yaml
kubectl apply -f /tmp/shopping-cart-deployment.yaml
kubectl apply -f k8s/shopping-cart-service.yaml
kubectl -n devops-exercise-10 rollout status deployment/product-catalog --timeout=180s
kubectl -n devops-exercise-10 rollout status deployment/shopping-cart --timeout=180s
kubectl -n devops-exercise-10 get deployments,pods,services -o wide
kubectl -n devops-exercise-10 get pods -o wide
kubectl -n devops-exercise-10 get endpoints
```

The actual pod image pulls across the three nodes and `kubectl get pods -o wide` are the evidence that the nodes can retrieve the images. If any pod shows `ImagePullBackOff`, check that both packages are public or that the cluster has a configured private-registry pull secret. Do not put registry credentials in a manifest.

## 5. Verify replica readiness and placement

```bash
chmod +x scripts/verify-cluster.sh scripts/test-endpoints.sh
./scripts/verify-cluster.sh
kubectl get nodes -o wide
kubectl -n devops-exercise-10 get deployments,pods,services -o wide
kubectl -n devops-exercise-10 get pods -o wide
kubectl -n devops-exercise-10 get endpoints
```

`verify-cluster.sh` exits nonzero unless Catalog has two Ready pods on two distinct nodes, Cart has three Ready pods on three distinct nodes, the Deployment counts match, and both Services have ready endpoints.

## 6. Test live endpoints and cart state

```bash
./scripts/test-endpoints.sh
```

The script uses temporary local `kubectl port-forward` processes, checks `/products` against all three expected items, checks `/cart` through its Service, then sends POST and GET through a port-forward to the same Cart pod so the in-memory state check is deterministic. It stops only the port-forward processes that it started. If local ports 18080–18082 are occupied in Killercoda, set `CATALOG_PORT`, `CART_SERVICE_PORT`, and/or `CART_POD_PORT` to free ports before running it.

For a manual POST/GET in the remote Linux terminal, choose one Cart pod and port-forward that pod:

```bash
POD="$(kubectl -n devops-exercise-10 get pods -l app.kubernetes.io/name=shopping-cart -o jsonpath='{.items[0].metadata.name}')"
kubectl -n devops-exercise-10 port-forward "pod/$POD" 18082:8080 >/tmp/cart-port-forward.log 2>&1 &
PF_PID=$!
for i in $(seq 1 20); do curl -fsS http://127.0.0.1:18082/health >/dev/null && break; sleep 1; done
curl -i -H 'Content-Type: application/json' -d '{"product_id":1,"name":"Laptop","price":1200,"quantity":1}' http://127.0.0.1:18082/cart
curl -i http://127.0.0.1:18082/cart
kill "$PF_PID"; wait "$PF_PID" 2>/dev/null || true
```

Do not interpret differing cart contents through the three-replica Service as shared storage: each pod has its own volatile memory and restarts clear it.

## 7. Demonstrate self-healing

Capture the initial five-pod healthy state before deleting anything. Then run each controlled test:

```bash
kubectl -n devops-exercise-10 get pods -l app.kubernetes.io/name=product-catalog -o wide
OLD_CATALOG="$(kubectl -n devops-exercise-10 get pods -l app.kubernetes.io/name=product-catalog -o jsonpath='{.items[0].metadata.name}')"
kubectl -n devops-exercise-10 delete pod "$OLD_CATALOG"
kubectl -n devops-exercise-10 rollout status deployment/product-catalog --timeout=180s
kubectl -n devops-exercise-10 get pods -l app.kubernetes.io/name=product-catalog -o wide
./scripts/verify-cluster.sh

kubectl -n devops-exercise-10 get pods -l app.kubernetes.io/name=shopping-cart -o wide
OLD_CART="$(kubectl -n devops-exercise-10 get pods -l app.kubernetes.io/name=shopping-cart -o jsonpath='{.items[0].metadata.name}')"
kubectl -n devops-exercise-10 delete pod "$OLD_CART"
kubectl -n devops-exercise-10 rollout status deployment/shopping-cart --timeout=180s
kubectl -n devops-exercise-10 get pods -l app.kubernetes.io/name=shopping-cart -o wide
./scripts/verify-cluster.sh
```

Record the deleted and replacement pod names and node assignments. A replacement is a pass only after it is Ready and the distinct-node check still passes.

## 8. Capture final state and preserve evidence

Before the playground expires, run and capture:

```bash
date -Is
kubectl config current-context
kubectl get nodes -o wide
kubectl -n devops-exercise-10 get deployments,pods,services -o wide
kubectl -n devops-exercise-10 get endpoints
./scripts/verify-cluster.sh
```

In the browser, show the Killercoda terminal with each command and its real output, then use Windows **Win+Shift+S** to capture the required evidence into the local `evidence/screenshots/` folder. Use the filenames in `evidence/screenshot-checklist.md`. Open every image locally and inspect its text, URL/terminal context, and visible contents. Save/copy the final command output into the local `evidence/verification.txt` before the remote session expires. Do not mark remote checks or screenshots passed until you have the actual outputs and images.

## 9. Safe cleanup in the remote playground

The session is disposable; it expires automatically. If cleanup is desired before it expires, remove only this namespace:

```bash
kubectl delete namespace devops-exercise-10
```

Do not run cleanup against the local Windows context. Never use `minikube delete`, and never stop or modify the existing local Minikube profile.

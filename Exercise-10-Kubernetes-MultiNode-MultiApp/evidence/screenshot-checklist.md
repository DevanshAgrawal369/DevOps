# Exercise 10 screenshot checklist

Only genuine captures from the actual Kubernetes playground or running service count as evidence. Each image must be opened and checked before its status can be changed to PASS.

| Required screenshot | Captured | Opened | Visually inspected | Complete | What it must show |
| --- | --- | --- | --- | --- | --- |
| `01-remote-cluster-three-nodes.png` | PENDING | PENDING | PENDING | PENDING | Actual remote `kubectl get nodes -o wide` with three Ready nodes. |
| `02-container-images-accessible.png` | PENDING | PENDING | PENDING | PENDING | Both image references and successful image availability in the remote cluster. |
| `03-product-catalog-source.png` | PENDING | PENDING | PENDING | PENDING | Actual `app-a-product-catalog/app.py` source. |
| `04-shopping-cart-source.png` | PENDING | PENDING | PENDING | PENDING | Actual `app-b-shopping-cart/app.py` source. |
| `05-kubernetes-deployments-and-services.png` | PENDING | PENDING | PENDING | PENDING | Applied manifests or live Deployments/Services showing required replica counts and anti-affinity. |
| `06-all-five-pods-ready.png` | PENDING | PENDING | PENDING | PENDING | Five Running and Ready application pods at the same time. |
| `07-pods-distributed-across-three-nodes.png` | PENDING | PENDING | PENDING | PENDING | `kubectl get pods -o wide` showing two Catalog and three Cart pods on distinct nodes. |
| `08-product-catalog-live-response.png` | PENDING | PENDING | PENDING | PENDING | Live Kubernetes-backed `/products` HTTP 200 JSON response. |
| `09-shopping-cart-get-response.png` | PENDING | PENDING | PENDING | PENDING | Live Kubernetes-backed `/cart` JSON response. |
| `10-shopping-cart-post-and-confirmation.png` | PENDING | PENDING | PENDING | PENDING | HTTP 201 POST and subsequent GET from the same Cart pod showing the item. |
| `11-services-and-endpoints.png` | PENDING | PENDING | PENDING | PENDING | Both Services and non-empty ready endpoints. |
| `12-product-catalog-self-healing.png` | PENDING | PENDING | PENDING | PENDING | Deleted Catalog pod and Ready replacement with desired count restored. |
| `13-shopping-cart-self-healing.png` | PENDING | PENDING | PENDING | PENDING | Deleted Cart pod and Ready replacement with desired count restored. |
| `14-final-healthy-cluster.png` | PENDING | PENDING | PENDING | PENDING | Final three-node placement and all five replicas Ready. |

No screenshots have been captured for this exercise yet. The local browser automation surface was unavailable, and no remote playground session has been started or observed. Do not rename, fabricate, or copy another person's screenshots into this directory.

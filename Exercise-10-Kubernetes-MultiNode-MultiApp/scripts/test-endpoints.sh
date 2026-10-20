#!/usr/bin/env bash
set -Eeuo pipefail

NAMESPACE="${NAMESPACE:-devops-exercise-10}"
KUBE_CONTEXT="${KUBE_CONTEXT:-$(kubectl config current-context)}"
K=(kubectl --context "$KUBE_CONTEXT")
CATALOG_PORT="${CATALOG_PORT:-18080}"
CART_SERVICE_PORT="${CART_SERVICE_PORT:-18081}"
CART_POD_PORT="${CART_POD_PORT:-18082}"
PIDS=()
TMP_DIR="$(mktemp -d)"

stop_forwards() {
    local pid
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
        wait "$pid" 2>/dev/null || true
    done
    PIDS=()
}

cleanup() {
    stop_forwards
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT INT TERM

start_forward() {
    local target="$1" mapping="$2" logfile="$3" local_port="$4"
    if command -v ss >/dev/null 2>&1 && ss -ltn | awk '{print $4}' | grep -Eq ":${local_port}$"; then
        echo "Local port $local_port is already listening; set the corresponding *_PORT variable." >&2
        exit 1
    fi
    "${K[@]}" -n "$NAMESPACE" port-forward "$target" "$mapping" >"$logfile" 2>&1 &
    PIDS+=("$!")
    for _ in $(seq 1 30); do
        if curl --silent --show-error --fail "http://127.0.0.1:${local_port}/health" >/dev/null 2>&1; then
            return 0
        fi
        sleep 1
    done
    cat "$logfile" >&2
    echo "Port-forward to $target did not become ready." >&2
    return 1
}

echo '== Product Catalog Service GET /products =='
start_forward svc/product-catalog-service "${CATALOG_PORT}:8080" "$TMP_DIR/catalog.log" "$CATALOG_PORT"
curl --silent --show-error --fail "http://127.0.0.1:${CATALOG_PORT}/products" | tee "$TMP_DIR/products.json" | python3 -c '
import json,sys
payload=json.load(sys.stdin)
expected={"products":[{"id":1,"name":"Laptop","price":1200},{"id":2,"name":"Phone","price":800},{"id":3,"name":"Headphones","price":150}]}
assert payload == expected, payload
print("PASS: exact three-product response")
'
stop_forwards

echo '== Shopping Cart Service basic GET /cart =='
start_forward svc/shopping-cart-service "${CART_SERVICE_PORT}:8080" "$TMP_DIR/cart-service.log" "$CART_SERVICE_PORT"
curl --silent --show-error --fail "http://127.0.0.1:${CART_SERVICE_PORT}/cart" | tee "$TMP_DIR/cart-service.json" | python3 -c 'import json,sys; value=json.load(sys.stdin); assert isinstance(value.get("items"),list), value; print("PASS: Service returned JSON cart response")'
stop_forwards

echo '== Deterministic Shopping Cart POST/GET against one pod =='
CART_POD="$("${K[@]}" -n "$NAMESPACE" get pods -l app.kubernetes.io/name=shopping-cart -o jsonpath='{.items[0].metadata.name}')"
if [[ -z "$CART_POD" ]]; then echo 'No shopping-cart pod found.' >&2; exit 1; fi
start_forward "pod/$CART_POD" "${CART_POD_PORT}:8080" "$TMP_DIR/cart-pod.log" "$CART_POD_PORT"
body='{"product_id":1,"name":"Laptop","price":1200,"quantity":1}'
status="$(curl --silent --show-error -o "$TMP_DIR/post.json" -w '%{http_code}' -H 'Content-Type: application/json' -d "$body" "http://127.0.0.1:${CART_POD_PORT}/cart")"
cat "$TMP_DIR/post.json"
if [[ "$status" != 201 ]]; then echo "Expected HTTP 201 from POST; received $status." >&2; exit 1; fi
curl --silent --show-error --fail "http://127.0.0.1:${CART_POD_PORT}/cart" | tee "$TMP_DIR/cart-after-post.json" | python3 -c '
import json,sys
payload=json.load(sys.stdin)
expected={"items":[{"product_id":1,"name":"Laptop","price":1200,"quantity":1}]}
assert payload == expected, payload
print("PASS: POST item is visible on subsequent GET to the same pod")
'

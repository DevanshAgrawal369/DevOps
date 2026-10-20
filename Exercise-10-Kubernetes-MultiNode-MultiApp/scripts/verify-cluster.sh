#!/usr/bin/env bash
set -Eeuo pipefail

NAMESPACE="${NAMESPACE:-devops-exercise-10}"
KUBE_CONTEXT="${KUBE_CONTEXT:-$(kubectl config current-context)}"
K=(kubectl --context "$KUBE_CONTEXT")

echo "Context: $KUBE_CONTEXT"
echo "Namespace: $NAMESPACE"

ready_nodes="$("${K[@]}" get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\t"}{.spec.unschedulable}{"\n"}{end}' | awk -F '\t' '$2 == "True" && $3 != "true" { count++ } END { print count+0 }')"
if (( ready_nodes < 3 )); then
    echo "FAIL: need at least 3 Ready, schedulable nodes; found $ready_nodes." >&2
    exit 1
fi

check_deployment() {
    local name="$1" expected="$2" records ready_count unique_nodes endpoints
    records="$("${K[@]}" -n "$NAMESPACE" get pods -l "app.kubernetes.io/name=$name" \
        -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.nodeName}{"\t"}{.status.phase}{"\t"}{range .status.conditions[?(@.type=="Ready")]}{.status}{end}{"\n"}{end}')"
    printf '\nPods for %s:\n%s\n' "$name" "$records"
    ready_count="$(printf '%s\n' "$records" | awk -F '\t' '$1 != "" && $3 == "Running" && $4 == "True" { count++ } END { print count+0 }')"
    unique_nodes="$(printf '%s\n' "$records" | awk -F '\t' '$1 != "" && $3 == "Running" && $4 == "True" { nodes[$2]=1 } END { print length(nodes) }')"
    if (( ready_count != expected )); then
        echo "FAIL: $name has $ready_count Ready pods; expected $expected." >&2
        return 1
    fi
    if (( unique_nodes != expected )); then
        echo "FAIL: $name spans $unique_nodes node(s); expected $expected distinct nodes." >&2
        return 1
    fi

    local counts
    counts="$("${K[@]}" -n "$NAMESPACE" get deployment "$name" \
        -o jsonpath='{.spec.replicas}{" "}{.status.updatedReplicas}{" "}{.status.availableReplicas}{" "}{.status.readyReplicas}')"
    if [[ "$counts" != "$expected $expected $expected $expected" ]]; then
        echo "FAIL: deployment/$name replica counts are '$counts'; expected '$expected $expected $expected $expected'." >&2
        return 1
    fi

    local service
    if [[ "$name" == "product-catalog" ]]; then service=product-catalog-service; else service=shopping-cart-service; fi
    endpoints="$("${K[@]}" -n "$NAMESPACE" get endpoints "$service" \
        -o jsonpath='{range .subsets[*]}{range .addresses[*]}{.ip}{" "}{end}{end}')"
    if [[ -z "${endpoints// /}" ]]; then
        echo "FAIL: $service has no ready endpoints." >&2
        return 1
    fi
    echo "PASS: $name ready=$ready_count distinct_nodes=$unique_nodes deployment_counts='$counts' endpoints='$endpoints'"
}

"${K[@]}" get nodes -o wide
check_deployment product-catalog 2
check_deployment shopping-cart 3
"${K[@]}" -n "$NAMESPACE" get deployments,pods,services -o wide
"${K[@]}" -n "$NAMESPACE" get endpoints
echo 'PASS: replica readiness, distinct-node placement, and service endpoints verified.'

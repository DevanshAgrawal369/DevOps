# Local screenshot evidence audit

Screenshots created from the actual local services using Playwright and visually inspected on 2026-10-20. Temporary port forwards for Kubernetes services used host ports 18081 and 18083 and were terminated after capture. Existing port-forward 8080 was preserved.
| Filename | Purpose | Status |
|---|---|---|
| `nginx-page.png` | Earlier Nginx page capture | Present; previously visually inspected |
| `screenshots/01-nginx-live.png` | Live Nginx welcome page served by current `hello-k8s` Pod via temporary port-forward | PASS — visually inspected |

The image is a rendered browser page; the live HTTP response was 200. This is evidence of the current Nginx Pod and Service, not proof that every historical manifest is still deployed unchanged.

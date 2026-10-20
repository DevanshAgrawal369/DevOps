# Screenshot checklist

No Jenkins screenshots were captured. The observed environment has no Jenkins container/process, `localhost:8081` is unavailable, and port 8080 is an existing Minikube port-forward returning HTTP 404. Capturing another page as Jenkins evidence would be misleading.

| Required filename | Purpose | Status | What to capture when Jenkins is available |
|---|---|---|---|
| `01-jenkins-container.png` | Running Jenkins container and published ports | BLOCKED | PowerShell terminal with `docker ps --filter "name=jenkins" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"`; ensure no secrets are visible. |
| `02-jenkins-setup.png` | Genuine first-time setup/plugin stage | BLOCKED | Jenkins setup wizard only if that stage is actually active; otherwise do not create a substitute screenshot. |
| `03-jenkins-dashboard.png` | Actual Jenkins dashboard | BLOCKED | Open the verified Jenkins URL after setup/login; show Jenkins UI and address bar, with no credentials visible. |
| `04-jenkins-version.png` | Version from the actual installation | BLOCKED | Show Jenkins Manage Jenkins/System Information version page or actual running container version output. |
| `05-jenkins-access-verification.png` | Successful HTTP access | BLOCKED | Show a successful response from the verified Jenkins URL (for example, `Invoke-WebRequest` status or Jenkins page). Do not use the unrelated 8080 HTTP 404. |

Save genuine captures using the exact filenames in `evidence/screenshots/`, inspect each image for readability and secrets, then change the corresponding statuses here and record the actual verification in `verification.txt`.

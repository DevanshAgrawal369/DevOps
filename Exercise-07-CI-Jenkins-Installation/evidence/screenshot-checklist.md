# Exercise 7 screenshot checklist

Screenshots were captured from the local Jenkins container and Microsoft Edge via Playwright on 2026-10-20. Every existing image below was visually opened and checked for legibility and exposed credentials. The setup wizard is now complete.

| File | Purpose | Status |
|---|---|---|
| `screenshots/01-jenkins-unlock.png` | Initial unlock page; password input is blank | PASS — inspected |
| `screenshots/02-jenkins-plugin-selection.png` | Suggested-plugin setup screen | PASS — inspected |
| `screenshots/03-jenkins-plugin-progress.png` | Plugin installation progress | PASS — inspected |
| `screenshots/04-jenkins-admin-setup-choice.png` | First-admin choice; blank credential fields and continue-as-admin option | PASS — inspected |
| `screenshots/05-jenkins-instance-configuration.png` | Jenkins URL configured as `http://localhost:8081/` | PASS — inspected |
| `screenshots/06-jenkins-ready.png` | Setup completion screen | MISSING — the wizard advanced before this screen was captured |
| `screenshots/07-jenkins-dashboard.png` | Actual Jenkins dashboard | PASS — inspected |
| `screenshots/08-jenkins-version.png` | Actual Jenkins version page | PASS — inspected; 2.580.1 |
| `screenshots/01-jenkins-container.png` | Terminal showing container and local port mapping | MISSING — verified in text evidence, no terminal screenshot captured |
| `screenshots/05-jenkins-access-verification.png` | Successful HTTP check | MISSING — HTTP 200 recorded in text evidence; no separate screenshot |

The Jenkins UI captures contain no administrator password. Port 8080 remains the existing Minikube port-forward; Jenkins is isolated on `127.0.0.1:8081`.

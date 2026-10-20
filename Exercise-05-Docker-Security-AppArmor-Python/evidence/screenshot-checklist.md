# Screenshot checklist

| Filename | Purpose | Status |
|---|---|---|
| `screenshots/01-flask-app-unconfined.png` | Flask response from the Exercise 5 image, run temporarily on loopback port 15005 | PASS — visually inspected; HTTP 200 |
| AppArmor enforcement screenshot | Loaded profile and denial event from Docker daemon's Linux host | BLOCKED — Docker Desktop VM profile loading/enforcement was not demonstrated |

The temporary container was removed immediately after capture. This image proves the application response only. It is not evidence that `my-apparmor-profile` was loaded or enforced; existing text evidence records that the effective profile was `kernel`.

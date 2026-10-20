# Screenshot checklist

| Filename | Purpose | Status |
|---|---|---|
| `Containers_list.png` | Existing container inventory capture | Present; previously visually inspected |
| `screenshots/01-api-live.png` | Actual Flask `/about` JSON response | PASS — visually inspected; HTTP 200 |

Read-only container inspection confirmed `flask`, `redis`, and `mysql` are attached to `my-bridge-net`. API success is visually demonstrated; the previous container list alone does not prove network connectivity.

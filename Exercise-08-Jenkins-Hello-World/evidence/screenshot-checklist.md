# Screenshot checklist

All captures are genuine browser-rendered pages from the public GitHub repository and the running local Jenkins instance, captured with Microsoft Edge through Playwright on 2026-10-20. Each file was opened and visually inspected for correctness, readability, and visible secrets.

| Filename | Evidence | Status |
|---|---|---|
| `01-github-repository.png` | Public `devops-sample-code` repository, `main` branch, and `hello-world.sh` file listing | CAPTURED — visually inspected |
| `02-hello-world-script.png` | Published script with Bash shebang and exact echo statement | CAPTURED — visually inspected |
| `03-jenkins-job-configuration.png` | Freestyle job with Git URL, `*/main`, no credentials, description, and shell command | CAPTURED — visually inspected |
| `04-jenkins-dashboard.png` | Jenkins dashboard showing HelloWorld and successful build #1 | CAPTURED — visually inspected |
| `05-jenkins-successful-build.png` | Build #1 status page showing Success and the checked-out repository/commit | CAPTURED — visually inspected |
| `06-jenkins-console-output.png` | Actual checkout log, `sh hello-world.sh`, `Hello, Jenkins!`, and `Finished: SUCCESS` | CAPTURED — visually inspected |

No requested screenshot is missing. The images contain no password or token values.

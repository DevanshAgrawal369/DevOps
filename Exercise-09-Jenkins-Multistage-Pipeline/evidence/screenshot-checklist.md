# Exercise 9 screenshot checklist

Captured means a genuine image file exists. Visual inspection means the image was opened and checked for readability, correctness, and visible sensitive data.

| Required image | Captured | Visually inspected | What it proves / limitation |
| --- | --- | --- | --- |
| `01-github-repository.png` | PASS | PASS | Public GitHub repository listing shows the Flask source, tests, requirements, Jenkinsfile, and preserved `hello-world.sh`. |
| `02-flask-source.png` | PASS | PASS | Actual published `app.py` content on GitHub. |
| `03-jenkinsfile-stages.png` | PASS | PASS | Actual published Jenkinsfile; the readable capture shows Build, Test, Code Quality, Deploy, Run Application, and Test Application stages. |
| `04-jenkins-pipeline-job.png` | BLOCKED | BLOCKED | Requires authenticated Jenkins job configuration; the current account credential is unavailable. |
| `05-jenkins-stage-view.png` | BLOCKED | BLOCKED | No Exercise 9 Jenkins build exists. Pipeline Stage View plugin was absent at inspection. |
| `06-jenkins-console-output.png` | BLOCKED | BLOCKED | Requires the real Jenkins build console. |
| `07-flask-response.png` | PASS (local smoke only) | PASS | Real browser page response from the published app running in a temporary, non-root local Docker smoke container. HTTP 200 and exact body. It is not a Jenkins deployment screenshot. |
| `08-test-results.png` | BLOCKED | BLOCKED | No Jenkins test/lint stage output exists. Actual unit/lint results are in `verification.txt`, but not presented as a Jenkins screenshot. |

The four captured images were opened and inspected. No passwords, tokens, Jenkins cookies, or hashes are visible. The exercise remains incomplete until an authenticated Jenkins run succeeds and the blocked Jenkins screenshots are captured.

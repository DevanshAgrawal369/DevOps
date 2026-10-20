# Exercise 9 — Jenkins Multi-Stage Pipeline for a Python Flask Application

## Objective and current status

This exercise defines a Jenkins Declarative Pipeline that builds a Flask application, runs unit tests and Flake8, copies the application into a workspace deployment directory, starts it on a checked local port, verifies a live HTTP response, and cleans up its process.

The source is in the existing public [devops-sample-code repository](https://github.com/DevanshAgrawal369/devops-sample-code), separate from this DevOps repository. The source commit is `b36bc1a00816ad97357244ec822e8d4735be0cd5`.

**Jenkins execution is currently blocked by authentication.** The existing Jenkins controller is running at `http://localhost:8081`, but administrator authentication remains unresolved. The `Python-MultiStage-Pipeline` Jenkins job has NOT been configured, and no Jenkins pipeline build has successfully executed. Anonymous API identity is confirmed. No password reset, account change, job creation, or existing job modification was performed. As a result, the Jenkins build, stage results, console output, Jenkins screenshots, and cleanup of a pipeline-launched app are not claimed as completed. See [`evidence/verification.txt`](evidence/verification.txt).

A separate ephemeral Docker smoke check and the two unit tests plus lint were run against the published source. These validate the source, not a Jenkins build.

## Architecture

```text
GitHub (public sample repository)
             |
             v
Jenkins Pipeline job (Python-MultiStage-Pipeline; not yet configured)
  Build -> Test -> Code Quality -> Deploy -> Run Application
                                             -> Test Application
             |
             v
Workspace-only deployment in a temporary directory; tracked process cleanup
```

The existing Jenkins controller has the Pipeline and Git plugins, but no Python executable, pip, Docker CLI, or Docker socket. The Jenkinsfile bootstraps a pinned `uv` binary into the Jenkins user's cache after verifying its SHA-256, then installs Python 3.12.10 and project dependencies in the job workspace. This avoids installing packages into the controller image or granting it Docker access.

## Source files

- `app.py` — Flask `/` route returning `Hello, Jenkins Multi-Stage Pipeline!`; port is configurable through `PORT` and defaults to 5000.
- `test_app.py` — two unittest checks for HTTP 200 and the exact response body.
- `requirements.txt` — pinned Flask, compatible Werkzeug, and Flake8 dependencies.
- `Jenkinsfile` — Declarative Pipeline with six real stages, a fixed local test port (51809) checked for conflicts, and a `post { always }` cleanup that verifies the tracked PID belongs to the deployed app before signaling it.
- `hello-world.sh` — Exercise 8 script preserved in the same sample repository.

The pipeline uses a workspace deployment folder named `python-app-deploy`; it does not publish a persistent production service. Its Flask process is only for the live test and should be removed in all build outcomes.

## Pipeline stages

1. **Build** downloads the pinned `uv` artifact, checks its SHA-256, installs Python 3.12.10 into the Jenkins user's tool cache, creates `.venv`, and installs pinned dependencies.
2. **Test** runs `python -m unittest -v` using `.venv`.
3. **Code Quality** runs the pinned Flake8 executable against `app.py` and `test_app.py`.
4. **Deploy** copies `app.py` and `requirements.txt` into `python-app-deploy` and checks both files.
5. **Run Application** checks that port 51809 is available, then starts the deployed app and records its PID in the build workspace.
6. **Test Application** polls the live endpoint, asserts HTTP 200 and the exact body, and prints the response.
7. **Post actions** report success/failure and stop only the process recorded by this build after checking its command line.

## Jenkins configuration and run instructions

Once an authenticated Jenkins session is available:

1. Open `http://localhost:8081` and create a **Pipeline** job named `Python-MultiStage-Pipeline`.
2. Under **Pipeline**, select **Pipeline script from SCM**, SCM **Git**, repository `https://github.com/DevanshAgrawal369/devops-sample-code.git`, branch `*/main`, and script path `Jenkinsfile`.
3. Leave credentials empty for this public repository.
4. Save, then select **Build Now**. Inspect every stage and the build console. A successful run must show two passing tests, a clean Flake8 invocation, deployment file checks, HTTP 200 with the exact response, process cleanup, and `Finished: SUCCESS`.

The Jenkins controller currently has the Pipeline plugin and Git plugin installed. The Pipeline Stage View plugin was not found during inspection. Jenkins UI access is blocked by the unavailable current administrator credential; the old initial-unlock password file is not a supported password-recovery mechanism. Do not reset the controller or alter its data to bypass this blocker.

## Verification performed

- The public repository contains `app.py`, `test_app.py`, `requirements.txt`, and `Jenkinsfile` at source commit `b36bc1a00816ad97357244ec822e8d4735be0cd5`; the Exercise 8 script remains present.
- Unit tests: **2 passed** in a temporary container using Python 3.12.12.
- Flake8: **7.3.0 passed** on both Python source files.
- The source-level Docker smoke check used the published files at commit `b36bc1a00816ad97357244ec822e8d4735be0cd5`, returned HTTP 200 with the expected message, and was stopped and removed. The screenshot is explicitly a local smoke test, not a Jenkins deployment.
- Jenkins itself: controller is running and responds at port 8081, but authenticated access returned HTTP 403 when using the stale initial-unlock credential. The anonymous identity endpoint reports `anonymous`. No pipeline job or build was created.

## Troubleshooting

- **Jenkins 403 / no login:** The file `secrets/initialAdminPassword` is only for initial unlock. It is not necessarily the current password. Sign in with the current authorized Jenkins account or use the supported administrator recovery procedure for this exact installation. Do not delete its container or persistent volume.
- **Python unavailable on controller:** This Jenkinsfile downloads a checksum-pinned `uv` binary and installs Python in the Jenkins user cache/workspace. It does not require system Python or Docker socket access. Network access to GitHub release assets and Python package indexes is required.
- **Port 51809 occupied:** The pipeline fails before launch instead of killing another process. Choose a different isolated port only after checking for a conflict and update the Jenkinsfile consistently.
- **Git checkout fails:** Confirm the sample repo remains public and configure no credentials unless repository access requirements change.
- **Flask response fails:** Review the live HTTP status/body and `app-server.log` in the Jenkins workspace; the `post` cleanup still targets only the PID recorded by that build.

## Evidence and remaining work

Screenshot statuses are tracked in [`evidence/screenshot-checklist.md`](evidence/screenshot-checklist.md). Captured and visually inspected: `01-github-repository.png`, `02-flask-source.png`, `03-jenkinsfile-stages.png`, and `07-flask-response.png`. The response screenshot is from the local Docker smoke test only. Jenkins job, stage, console, and pipeline-run screenshots remain blocked until Jenkins authentication is restored. The exercise is not complete until the real Jenkins Pipeline checks out this source and succeeds.

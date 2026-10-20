# Exercise 7 — Introduction to CI and Jenkins Installation

## Objective

Learn how Continuous Integration (CI) works, compare common CI/CD tools, and understand how Jenkins is installed and verified in Docker. This exercise documents the live Windows/Docker Desktop environment as it was inspected; it does not claim a Jenkins instance was available when it was not.

## Continuous Integration

Continuous Integration is the practice of merging small code changes into a shared repository frequently and automatically checking each change. A CI system detects a commit or pull request, prepares its build environment, resolves dependencies, runs checks and tests, then reports success or failure quickly. CI helps teams find integration errors while changes are still small. Continuous Delivery extends this flow by keeping validated changes ready to release; Continuous Deployment automatically releases qualifying changes.

### Features

- **Frequent integration:** developers commit and push small changes regularly.
- **Automated builds:** the CI worker checks out source and creates the build artifact.
- **Automated testing:** unit, integration, and other checks run consistently.
- **Immediate feedback:** results are reported to the developer and repository.

### Benefits

- Finds defects and integration problems earlier.
- Makes collaboration easier by integrating changes continuously.
- Shortens development feedback cycles.
- Improves code quality through repeatable checks.

### Typical CI workflow

1. A developer commits and pushes code or opens a pull request.
2. A CI server detects the repository event.
3. A worker checks out the revision and resolves dependencies.
4. The configured build and automated tests run.
5. The server reports success or failure, with logs for diagnosis.

## CI/CD tools

The tools below cover the products listed in the exercise handout. Their capabilities and hosting models differ; select one based on repository, infrastructure, security, and team needs.

| Tool | Overview and notable features | A good fit for | Website |
|---|---|---|---|
| GitLab CI/CD | Repository-integrated pipelines defined in `.gitlab-ci.yml`, jobs, stages, runners, artifacts, and reusable components. | Teams hosting source or managing the full software lifecycle in GitLab. | [gitlab.com](https://about.gitlab.com/solutions/continuous-integration/) |
| CircleCI | Hosted CI/CD pipelines configured in a repository, with reusable configuration and parallel execution options. | Teams wanting managed build infrastructure and a focused pipeline service. | [circleci.com](https://circleci.com/) |
| Travis CI | Hosted build and test automation configured with a `.travis.yml` file and build matrix. | Projects that want a straightforward hosted CI workflow across supported repositories. | [travis-ci.com](https://www.travis-ci.com/) |
| Bamboo | Atlassian's CI/CD server, with build plans, deployment projects, agents, and integrations across Atlassian products. | Organizations already using Atlassian tools and needing self-managed CI/CD. | [atlassian.com/software/bamboo](https://www.atlassian.com/software/bamboo) |
| TeamCity | JetBrains CI/CD server with build configurations, agents, build chains, and Kotlin DSL configuration. | Teams seeking a self-managed CI server with a visual build configuration experience. | [jetbrains.com/teamcity](https://www.jetbrains.com/teamcity/) |
| Azure DevOps | Microsoft's developer services, including Azure Pipelines, repos, boards, and artifacts; supports cloud-hosted and self-hosted agents. | Organizations using Azure or needing pipelines across many languages and platforms. | [azure.microsoft.com/products/devops](https://azure.microsoft.com/products/devops) |
| GitHub Actions | Workflow automation close to GitHub repositories, configured in YAML, using hosted or self-hosted runners and reusable actions. | Projects already hosted on GitHub that want repository-native automation. | [github.com/features/actions](https://github.com/features/actions) |
| Spinnaker | Open-source, multi-cloud continuous delivery platform focused on application deployment and release orchestration. | Teams orchestrating deployments across cloud providers; it is more delivery-oriented than a basic CI build service. | [spinnaker.io](https://spinnaker.io/) |
| Buildkite | CI/CD orchestration service that runs jobs on agents managed by the team, with pipeline-as-code and parallel jobs. | Teams that want a hosted control plane while running builds on their own infrastructure. | [buildkite.com](https://buildkite.com/) |
| Drone | Container-native CI/CD platform with pipelines described in YAML and execution by runner infrastructure. | Teams preferring a container-oriented, self-hosted pipeline setup. | [drone.io](https://www.drone.io/) |

## Jenkins

Jenkins is an extensible automation server used to build, test, and deliver software. It can run on a developer machine or shared infrastructure, connect to source-control events, and execute repeatable workflows using agents. The controller hosts the web interface and coordinates work; agents run build steps.

### Core concepts

- **Jobs/projects:** saved definitions for automated work.
- **Builds:** individual executions of a job, with status, timing, and logs.
- **Pipelines:** stages and steps expressed as code, commonly in a `Jenkinsfile`.
- **Plugins:** extensions that add integrations, credentials providers, reports, and other features.
- **Nodes and agents:** machines or containers that execute work for the controller.

## Docker installation and first access

This section is a reproducible reference for a compatible setup. **Do not run a second Jenkins instance on this machine without first resolving the environment blocker below.** The observed port 8080 belongs to an existing Minikube `kubectl port-forward`, so the sample command uses loopback port 8081 and a named persistent volume. Check that both the name and port are unused before creating anything.

In PowerShell, after confirming there is no existing Jenkins setup to reuse and choosing to create one:

```powershell
docker volume create jenkins_home
docker run -d --name jenkins-exercise7 `
  --restart unless-stopped `
  -p 127.0.0.1:8081:8080 -p 127.0.0.1:50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  jenkins/jenkins:lts-jdk21
```

The official Jenkins image and an explicitly chosen LTS/JDK tag are used. Keep the data volume: it contains Jenkins configuration, plugins, and jobs. Do not remove or replace a volume to fix a setup problem. Open `http://localhost:8081` only for this sample instance. To reuse an existing installation, use its already configured URL instead.

### Initial administrator password

The setup wizard may request an initial unlock password. Retrieve it only when the selected container is genuinely at that stage, using a private interactive PowerShell session:

```powershell
docker exec -it jenkins-exercise7 cat /var/jenkins_home/secrets/initialAdminPassword
```

Enter the displayed value only into that Jenkins setup page. Do not put it in a command transcript, screenshot, evidence file, chat, or Git. If an established Jenkins account already exists, sign in with that account instead; do not reset it for this exercise.

In the wizard, install the suggested plugins or select plugins appropriate to the lab, then create an administrator using credentials chosen by the system owner. Complete the wizard and confirm that the Jenkins dashboard opens. No account should be invented or password committed for the purpose of a demonstration.

### Verify an installation

Use the actual mapped port and container name:

```powershell
docker ps --filter "name=jenkins" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Invoke-WebRequest -Uri http://localhost:8081/login -MaximumRedirection 0
docker exec jenkins-exercise7 java -jar /usr/share/jenkins/jenkins.war --version
```

An HTTP response alone proves only that a web server responded. Check the container image/name and port mapping, inspect the actual Jenkins UI, and verify its version from the running installation. A redirect to login can be normal. Do not confuse another service's HTTP response on 8080 with Jenkins.

## Verification in this environment

Inspection was performed from Windows PowerShell on 2026-10-20. Docker Desktop's Linux engine answered successfully (Docker client/server 29.5.2, context `desktop-linux`). No container matching Jenkins was present in `docker ps -a`, and no Jenkins or Java process was found on the Windows host. Port 8080 was listening under `kubectl.exe`; `http://localhost:8080/login` returned HTTP 404, so that endpoint is the existing Minikube port-forward and is not a Jenkins interface. Port 8081 was not reachable. No Jenkins version, setup page, or dashboard could therefore be verified.

The Exercise 6 delivery, Prometheus, and Grafana containers were running during inspection. They were left untouched. No new Jenkins container, volume, or account was created. See [`evidence/verification.txt`](evidence/verification.txt) and [`evidence/screenshot-checklist.md`](evidence/screenshot-checklist.md) for exact outcomes. Screenshots requiring an actual Jenkins instance are marked BLOCKED; none were fabricated.

## Troubleshooting and cleanup

- **Port 8080 is occupied:** identify the owning process with `Get-NetTCPConnection -LocalPort 8080 -State Listen` and `Get-Process -Id <OwningProcess>`. Do not stop it unless its owner authorizes that action. Choose another loopback port for a new, approved demo.
- **Docker is unavailable:** check `docker version` and Docker Desktop's Linux engine/context before running Linux containers.
- **Jenkins page does not open:** check `docker ps`, the published host port, and container logs (`docker logs <jenkins-container>`). Logs can contain sensitive configuration; redact them before sharing.
- **Setup password is rejected:** ensure it is from the same Jenkins home volume and installation. Do not delete the volume or reset Jenkins as a workaround.
- **Plugins are slow:** allow the installation to finish and inspect Jenkins logs locally. Avoid exposing the setup page or credentials publicly.
- **Stop a demo you created:** `docker stop jenkins-exercise7` stops only that named container. Keep its volume if you may reuse the installation. Removing the container/volume is a separate data-affecting action and is intentionally not part of cleanup instructions here.

## Conclusion

CI gives developers fast, repeatable feedback on integrated changes. Jenkins provides a flexible automation server built from jobs, pipelines, plugins, and worker agents. In this inspection, Docker was healthy but Jenkins was unavailable, and port 8080 belonged to Minikube. The installation procedure and evidence checklist are ready for a later run when the existing Jenkins endpoint is available or a new instance is explicitly approved.

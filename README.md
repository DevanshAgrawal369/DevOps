\# DevOps Hands-On Exercises



A practical collection of DevOps lab exercises covering application development, version control, continuous integration and delivery, containerization, Kubernetes, and automated testing.



\## Table of Contents



1\. \[Kubernetes Pod and Service](#exercise-1-kubernetes-pod-and-service)

2\. \[Deploy a Flask Application on Minikube](#exercise-2-deploy-a-flask-application-on-minikube)

3\. \[Scale a Flask Application Using ReplicaSets](#exercise-3-scale-a-flask-application-using-replicasets)

4\. Jenkins Installation and Setup

5\. Continuous Integration and Delivery Using Jenkins

6\. Docker Commands and Container Management

7\. Develop and Containerize a Web Application

8\. Creating a Hello World Jenkins Job

9\. Jenkins Multi-Stage Pipeline for a Python Flask Application

10\. Automated Testing Using Selenium



\## Repository Structure



```text

DevOps/

├── README.md

├── Exercise-01-Kubernetes-Pod/

├── Exercise-02-Flask-Minikube/

├── Exercise-03-Flash-Sale-ReplicaSet/

├── Exercise-04-Docker-Networking/

├── Exercise-05-Docker-Security-AppArmor-Python/

├── Exercise-06-Real-Time-Operations-Monitoring-Alerting/

├── Exercise-07-CI-Jenkins-Installation/

├── Exercise-08-Jenkins-Hello-World/

├── Exercise-09-Jenkins-Multistage-Pipeline/

└── Exercise-10-Selenium-Automation/

```



\## Exercise 1: Kubernetes Pod and Service



\*\*Objective:\*\* Learn how to create a Kubernetes Pod and expose an application using a Service.



\*\*Technologies:\*\* Kubernetes, Minikube, kubectl, NGINX, YAML.



\*\*Tasks completed:\*\*

\- Created a Pod running NGINX.

\- Defined a Kubernetes Service using YAML.

\- Applied the configuration to Minikube.

\- Verified the Pod, Service, and endpoints.

\- Accessed the NGINX welcome page.

\- Saved verification output and a screenshot.



\*\*Key learning outcomes:\*\* Pods, labels, selectors, Services, endpoints, and Kubernetes resource management.



Directory: `Exercise-01-Kubernetes-Pod/`



\## Exercise 2: Deploy a Flask Application on Minikube



\*\*Objective:\*\* Containerize a Python Flask application and deploy it to a local Kubernetes cluster.



\*\*Technologies:\*\* Python, Flask, Docker, Kubernetes, Minikube, kubectl.



\*\*Tasks completed:\*\*

\- Created a Flask application.

\- Built a Docker image.

\- Loaded the image into Minikube.

\- Created a Kubernetes Deployment and NodePort Service.

\- Verified Pod readiness, deployment status, and application logs.

\- Tested the application through HTTP.

\- Saved verification output and a screenshot.



\*\*Application response:\*\*



`Hello from Flask on Kubernetes!`



\*\*Key learning outcomes:\*\* Docker image creation, local image loading, Deployments, Services, rollout verification, and application testing.



Directory: `Exercise-02-Flask-Minikube/`



\## Exercise 3: Scale a Flask Application Using ReplicaSets



\*\*Objective:\*\* Understand ReplicaSets, scaling, Pod placement, and self-healing using a simulated e-commerce flash-sale application.



\*\*Technologies:\*\* Python, Flask, Gunicorn, Docker, Kubernetes, Minikube.



\*\*Application endpoints:\*\*

\- `/` — Displays the Big Sale welcome message and serving Pod hostname.

\- `/buy?user=123` — Simulates a purchase and returns the product, user, and serving Pod.

\- `/health` — Returns application health information.



\*\*Tasks completed:\*\*

\- Built and loaded the Flash Sale Docker image.

\- Created a ReplicaSet with three replicas.

\- Exposed the application using a ClusterIP Service.

\- Configured readiness and liveness probes.

\- Tested the application endpoints.

\- Scaled the ReplicaSet from three to five Pods.

\- Deleted a Pod and verified automatic replacement.

\- Inspected Pod IPs, node placement, and ReplicaSet events.

\- Saved verification output.



\*\*Key learning outcomes:\*\* Desired replica counts, scaling, health probes, Service routing, and Kubernetes self-healing.



Directory: `Exercise-03-Flash-Sale-ReplicaSet/`



\## Exercise 4: Jenkins Installation and Setup



\*\*Objective:\*\* Install Jenkins and explore its interface and basic configuration.



\*\*Planned activities:\*\*

\- Set up Jenkins.

\- Complete the initial configuration.

\- Explore the Jenkins dashboard.

\- Configure basic tools and settings.

\- Create a sample job.



\*\*Key learning outcomes:\*\* Jenkins fundamentals, jobs, plugins, and build automation.



\## Exercise 5: Continuous Integration and Delivery Using Jenkins



\*\*Objective:\*\* Understand how Jenkins automates application builds and delivery workflows.



\*\*Planned activities:\*\*

\- Create a Jenkins job or pipeline.

\- Configure source-code integration.

\- Execute automated build steps.

\- Review build results and console logs.

\- Explore automated delivery stages.



\*\*Key learning outcomes:\*\* CI/CD concepts, pipelines, build automation, and feedback from automated jobs.



\## Exercise 6: Docker Commands and Container Management



\*\*Objective:\*\* Learn essential Docker commands for managing images and containers.



\*\*Planned activities:\*\*

\- Inspect Docker images and containers.

\- Pull images from a registry.

\- Run, stop, and remove containers.

\- Inspect container logs and configuration.

\- Tag and publish images.



\*\*Key learning outcomes:\*\* Container lifecycle management, image management, registries, and Docker CLI usage.



\## Exercise 7: Develop and Containerize a Web Application



\*\*Objective:\*\* Develop a simple web application and package it into a Docker image.



\*\*Planned activities:\*\*

\- Create the application source code.

\- Write a Dockerfile.

\- Build the application image.

\- Run and test the container.

\- Verify the application response.



\*\*Key learning outcomes:\*\* Dockerfiles, image layers, container ports, and reproducible application packaging.



\## Exercise 8: Creating a Hello World Jenkins Job



\*\*Objective:\*\* Publish a Bash script to GitHub and run it from a Jenkins Freestyle job.



\*\*Tasks completed:\*\*

\- Created and pushed `hello-world.sh` to the public `devops-sample-code` repository.

\- Configured the Jenkins `HelloWorld` Freestyle job to clone `main`.

\- Executed `sh hello-world.sh` in Jenkins build #1.

\- Verified `Hello, Jenkins!` and `Finished: SUCCESS` in Console Output.

\- Saved genuine GitHub and Jenkins screenshots in the exercise evidence folder.



\*\*Key learning outcomes:\*\* Git-based source checkout, Jenkins Freestyle jobs, shell build steps, and console verification.



\## Exercise 9: Jenkins Multi-Stage Pipeline for a Python Flask Application

\*\*Objective:\*\* Build, test, lint, deploy, and verify a Flask application through a Jenkins Declarative Pipeline.

\*\*Pipeline stages:\*\*

\- Create a Python virtual environment and install pinned dependencies.

\- Run Flask unit tests and Flake8 code-quality checks.

\- Copy the application into a workspace deployment directory.

\- Start the deployed application on a checked local port and verify its HTTP response.

\- Stop the build-owned application process during pipeline cleanup.

\*\*Source repository:\*\* `https://github.com/DevanshAgrawal369/devops-sample-code`

\*\*Verification status:\*\* Unit tests, lint, and a local Docker smoke check passed independently of Jenkins. Administrator authentication remains unresolved; the Jenkins pipeline job has NOT been configured or successfully executed. See `Exercise-09-Jenkins-Multistage-Pipeline/evidence/verification.txt`.

\*\*Key learning outcomes:\*\* Declarative pipelines, build stages, automated testing, linting, workspace deployment, live HTTP verification, and safe process cleanup.


\## Exercise 10: Automated Testing Using Selenium



\*\*Objective:\*\* Explore browser automation and test a web application using Selenium.



\*\*Planned activities:\*\*

\- Set up Selenium and a compatible browser driver.

\- Create a simple JavaScript program or web page as required by the lab.

\- Write automated browser tests.

\- Verify expected application behavior.

\- Record test results.



\*\*Key learning outcomes:\*\* Browser automation, test cases, automated verification, and regression testing.



\## Technologies Used



\- \*\*Version control:\*\* Git and GitHub

\- \*\*CI/CD:\*\* Jenkins

\- \*\*Containerization:\*\* Docker

\- \*\*Orchestration:\*\* Kubernetes and Minikube

\- \*\*Application development:\*\* Python and Flask

\- \*\*Web testing:\*\* Selenium

\- \*\*Configuration:\*\* YAML and Dockerfiles

\- \*\*Environment:\*\* Windows PowerShell and Docker Desktop



\## Getting Started



1\. Install the tools required by the specific exercise.

2\. Clone this repository.

3\. Open the relevant exercise folder.

4\. Read its README and inspect the configuration files.

5\. Follow the commands in the exercise instructions.

6\. Verify the results and save evidence.



```powershell

git clone https://github.com/DevanshAgrawal369/DevOps.git

cd DevOps

```



\## Learning Goals



\- Understand version control and repository organization.

\- Build and run containerized applications.

\- Deploy and manage applications with Kubernetes.

\- Learn automated build and delivery workflows.

\- Practice scaling and recovery of containerized workloads.

\- Explore automated testing and verification.

\- Document practical work with reproducible commands and evidence.




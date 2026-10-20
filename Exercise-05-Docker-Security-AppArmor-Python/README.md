# Exercise 5 — Docker Security with AppArmor and Python SDK

## Objective

Build a small Flask service and apply a custom AppArmor mandatory access control profile through Docker's Python SDK. The exercise separates a requested Docker security option from proof that the Linux kernel loaded and enforced the policy. AppArmor mediates access by a process in the container; it does not grant the container control over the Docker host's files.

## Architecture and files

- `app.py` serves one fixed response on port 5000.
- `Dockerfile` uses Python 3.12 slim, pins dependencies, and runs as the unprivileged `app` user.
- `apparmor/my-apparmor-profile` attaches to `/usr/local/bin/python3.12`, the executable explicitly launched by the image.
- `apply_apparmor.py` builds the image, requests the loaded profile, verifies PID 1's effective profile and the HTTP response, then removes its own container.
- `test_restricted_actions.py` performs controlled checks inside a profile-confined container.
- `evidence/` contains command output from this environment.

## Requirements

- Docker Engine with Linux containers and a reachable Docker API.
- For enforcement: a Linux Docker daemon with AppArmor enabled, `apparmor_parser`, permission to load profiles, and access to the host's AppArmor audit records. Docker Desktop's Linux VM is not necessarily configurable from Windows.
- Python 3.10+ on the client and dependencies from `requirements.txt` for the SDK scripts.

## Build and ordinary application check

From this folder:

```powershell
docker build -t flask-apparmor .
docker run --rm -d --name flask-apparmor-demo -p 5000:5000 flask-apparmor
curl.exe http://localhost:5000/
docker inspect flask-apparmor-demo
docker stop flask-apparmor-demo
```

Expected body: `Hello, this is a secure Flask application running inside a Docker container!`. The image uses a pinned `python:3.12.12-slim-bookworm` base and exact Flask and Docker SDK versions. Rebuild periodically to pick up base-image security updates.

## AppArmor policy

The profile's attachment path is the command used by `CMD`. It permits Python's runtime and packages, the application, certificates, basic system files and read-only process/system metadata needed by normal operation. Network stream access supports Flask. The explicit denials target container-local `/etc/passwd`, `/etc/shadow`, root's home, `/bin/bash` and its resolved `/usr/bin/bash` target, writes below `/sys`, and `CAP_SYS_ADMIN`/`CAP_SYS_MODULE`.

`/etc/passwd` in this policy is the container's file. A container-only profile does not restrict the host's `/etc/passwd`; host paths become relevant only if exposed to the container, for example through a bind mount. AppArmor rules supplement Docker's namespaces, capability set, seccomp policy, filesystem permissions and other controls. This profile is intentionally narrow and must be validated on the exact image and host before production use.

## Load and verify on a compatible Linux Docker host

Run on the Linux machine that hosts the Docker daemon (not merely in a container or in Windows):

```sh
sudo apparmor_parser -r -W apparmor/my-apparmor-profile
sudo aa-status | grep my-apparmor-profile
```

The parser must accept the file and `aa-status` must show it loaded. Then run `python apply_apparmor.py`. It creates the container with `apparmor:my-apparmor-profile`, inspects `HostConfig.SecurityOpt`, and reads `/proc/1/attr/current` inside the container. Both the requested option and the effective profile name must match. The script does not claim enforcement if either check fails. For denial attribution, inspect the Linux host's audit/kernel log after a denied operation, for example `sudo journalctl -k --since "5 minutes ago" | grep -i apparmor` or the distribution's audit log. The denial event should name the profile and operation. `docker inspect`'s requested `SecurityOpt` alone is not evidence of enforcement.

The loader must run in the same Linux kernel security environment as the Docker daemon. Never load the profile by modifying Docker Desktop VM internals or weakening VM controls.

## Python SDK scripts

Install the pinned client dependencies in a virtual environment if desired:

```sh
python -m pip install -r requirements.txt
python apply_apparmor.py
python test_restricted_actions.py
```

Both scripts use `docker.from_env()`, avoid taking over an existing predictable container name, do not fall back to an unconfined run, and remove only the container they created, including on errors. The action checker labels each result `PASS`, `FAIL`, or `BLOCKED`. A permission error is not conclusively an AppArmor denial without a corresponding host audit event. A missing `/bin/bash` is reported as missing, never as an AppArmor block.

## Current environment results and limits

This run used Windows 10 PowerShell 5.1 with Docker Desktop 4.76.0 and Docker 29.5.2, using the `desktop-linux` context and Linux kernel `6.6.87.2-microsoft-standard-WSL2`. Docker runtime feature metadata says `apparmor.enabled=true`, but `docker info` does not list AppArmor in its security options. Windows has no `apparmor_parser`; a read-only Alpine probe inside the daemon environment found no readable `/sys/kernel/security/apparmor/profiles` interface and no parser. The custom profile could not be loaded or independently confirmed. The SDK build and container start succeeded and Docker inspect retained `apparmor:my-apparmor-profile`, but `/proc/1/attr/current` reported `kernel`, so the SDK rejected the run and cleaned up. This is not proof of the intended profile being active. The ordinary unconfined container returned HTTP 200 with the expected response, ran as `app:app`, and used a random published host port. `/bin/bash` exists in this image. Restricted-action checks were all `BLOCKED` because the intended profile was not proven active; no `/etc/passwd` or bash denial is claimed. `apparmor_parser` syntax validation and audit-log denial correlation remain unavailable. See the evidence files for actual command output.

## Troubleshooting and cleanup

- `apparmor_parser: command not found`: run profile loading on a compatible Linux daemon host with AppArmor tools installed.
- `apparmor="..." not found` or OCI create failure: profile is not loaded into the daemon's kernel, or the daemon does not support custom profiles.
- Effective profile says `docker-default`, `unconfined`, or anything other than `my-apparmor-profile`: do not count the custom profile as applied.
- Port 5000 can be occupied for the manual demo; stop/remove `flask-apparmor-demo` after use. SDK scripts ask Docker for a random host port.
- SDK dependencies: `python -m pip install -r requirements.txt`.
- The scripts clean up their own test container. To inspect and remove a manually created demo, use `docker inspect flask-apparmor-demo` then `docker stop flask-apparmor-demo` and `docker rm flask-apparmor-demo`.

## Questions

1. **What is the purpose of using AppArmor with Docker containers?** AppArmor adds Linux kernel mandatory access control to the container process, limiting what files, capabilities, and operations it may access even if the application is compromised.
2. **How do AppArmor profiles help secure a Docker container?** A loaded profile applies an allow/deny policy to a process. Docker can request a profile at container creation; the kernel's effective process label and audit records provide stronger evidence that the profile was applied and that a denial occurred.
3. **Why restrict sensitive directories such as `/etc/` and `/var/`?** They can contain account data, credentials, configuration, logs, and mutable state. Restrict only paths the application does not need; broad denials can break runtime behavior. These paths refer to the container's filesystem unless host paths are mounted in.
4. **What other capabilities can be restricted using AppArmor profiles?** Policies can restrict capabilities such as `CAP_SYS_ADMIN`, `CAP_SYS_MODULE`, `CAP_NET_ADMIN`, `CAP_SYS_PTRACE`, and `CAP_DAC_OVERRIDE`, along with file access, execution, network families/types, mounts, signals, and other mediated operations. AppArmor capability rules do not replace Docker's capability bounding set.
5. **How can you verify if an AppArmor profile is successfully applied to a Docker container?** Confirm the profile is loaded on the daemon's Linux host, inspect Docker's requested `HostConfig.SecurityOpt`, and read `/proc/<container-pid>/attr/current` (or `/proc/1/attr/current` in the container) to check the effective profile. To prove a specific restriction fired, correlate the failed operation with an AppArmor denial in host audit/kernel logs. Requested configuration or a nonzero command exit code alone is insufficient.

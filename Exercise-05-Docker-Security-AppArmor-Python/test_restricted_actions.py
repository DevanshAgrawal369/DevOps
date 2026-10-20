"""Controlled Docker SDK checks; actions are run only in an AppArmor container."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import docker
import requests
from docker.errors import APIError, DockerException, NotFound

PROFILE = "my-apparmor-profile"
CONTAINER_NAME = "exercise5-restricted-actions"
IMAGE = "flask-apparmor"
EXPECTED = "Hello, this is a secure Flask application running inside a Docker container!"
ROOT = Path(__file__).resolve().parent


def main() -> int:
    client = None
    container = None
    created = False
    results: list[tuple[str, str]] = []
    try:
        client = docker.from_env()
        client.ping()
        if not any(tag == IMAGE for image in client.images.list() for tag in image.tags):
            print(f"Building missing image {IMAGE}")
            client.images.build(path=str(ROOT), tag=IMAGE, rm=True)
        try:
            client.containers.get(CONTAINER_NAME)
            raise RuntimeError(f"Container name collision: {CONTAINER_NAME} already exists; left untouched")
        except NotFound:
            pass
        try:
            container = client.containers.create(
                IMAGE, name=CONTAINER_NAME, detach=True,
                ports={"5000/tcp": None}, security_opt=[f"apparmor:{PROFILE}"],
                user="app:app",
            )
            created = True
            container.start()
        except APIError as exc:
            print(
                f"BLOCKED: Docker rejected requested AppArmor profile {PROFILE!r}; "
                "load it in the daemon's Linux host. No fallback used. " + str(exc),
                file=sys.stderr,
            )
            results.extend([
                ("/etc/passwd read", "BLOCKED: requested profile unavailable"),
                ("/bin/bash execution", "BLOCKED: requested profile unavailable"),
                ("Flask endpoint", "BLOCKED: requested profile unavailable"),
            ])
            for name, status in results:
                print(f"{status.split(':', 1)[0]}: {name} - {status.split(':', 1)[1].strip()}")
            return 2
        container.reload()
        requested = container.attrs.get("HostConfig", {}).get("SecurityOpt") or []
        code, out = container.exec_run(["cat", "/proc/1/attr/current"])
        effective = out.decode(errors="replace").strip().replace("\x00", "") if code == 0 else ""
        active = (f"apparmor:{PROFILE}" in requested and
                  (effective == PROFILE or effective.startswith(PROFILE + " ")))
        print(f"Requested SecurityOpt: {requested}")
        print(f"PID 1 effective profile: {effective or 'unavailable'}")
        if not active:
            results.extend([
                ("/etc/passwd read", "BLOCKED: intended profile not proven active"),
                ("/bin/bash execution", "BLOCKED: intended profile not proven active"),
                ("Flask endpoint", "BLOCKED: intended profile not proven active"),
            ])
        else:
            code, out = container.exec_run(["/bin/sh", "-c", "cat /etc/passwd"], user="app:app")
            if code == 0:
                results.append(("/etc/passwd read", "FAIL: read succeeded despite profile restriction"))
            elif "Permission denied" in out.decode(errors="replace"):
                results.append(("/etc/passwd read", "BLOCKED: read denied; AppArmor audit event required to attribute conclusively"))
            else:
                results.append(("/etc/passwd read", f"BLOCKED: unexpected error (exit {code}); not attributed to AppArmor"))

            code, out = container.exec_run(["/bin/sh", "-c", "if [ -x /bin/bash ]; then /bin/bash -c 'echo bash-ran'; else echo BASH_MISSING; exit 127; fi"], user="app:app")
            msg = out.decode(errors="replace").strip()
            if "BASH_MISSING" in msg:
                results.append(("/bin/bash execution", "BLOCKED: /bin/bash is absent; no AppArmor denial claimed"))
            elif code == 0:
                results.append(("/bin/bash execution", "FAIL: bash executed"))
            elif "Permission denied" in msg:
                results.append(("/bin/bash execution", "BLOCKED: execution denied; AppArmor audit event required to attribute conclusively"))
            else:
                results.append(("/bin/bash execution", f"BLOCKED: exit {code}, cause not proven to be AppArmor"))

            binding = container.attrs["NetworkSettings"]["Ports"]["5000/tcp"][0]
            try:
                response = requests.get(f"http://127.0.0.1:{binding['HostPort']}/", timeout=10)
                results.append(("Flask endpoint", "PASS" if response.status_code == 200 and response.text == EXPECTED else f"FAIL: HTTP {response.status_code}, body={response.text!r}"))
            except requests.RequestException as exc:
                results.append(("Flask endpoint", f"FAIL: {exc}"))
        for name, status in results:
            print(f"{status.split(':', 1)[0]}: {name} - {status.split(':', 1)[1].strip() if ':' in status else ''}")
        return 2 if any(status.startswith("BLOCKED") and "intended profile not proven active" in status for _, status in results) else (1 if any(status.startswith("FAIL") for _, status in results) else 0)
    except (DockerException, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    finally:
        if created and container is not None:
            try:
                container.stop(timeout=5)
            except Exception:
                pass
            try:
                container.remove()
                print(f"Removed script-created container {CONTAINER_NAME}")
            except Exception as exc:
                print(f"Cleanup warning for {CONTAINER_NAME}: {exc}", file=sys.stderr)
        if client is not None:
            client.close()


if __name__ == "__main__":
    raise SystemExit(main())

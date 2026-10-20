"""Build and run Flask only when the requested AppArmor profile is active."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import docker
import requests
from docker.errors import APIError, DockerException, NotFound

PROFILE = "my-apparmor-profile"
CONTAINER_NAME = "exercise5-flask-apparmor"
IMAGE = "flask-apparmor"
EXPECTED = "Hello, this is a secure Flask application running inside a Docker container!"
ROOT = Path(__file__).resolve().parent


def main() -> int:
    client = None
    container = None
    created = False
    try:
        client = docker.from_env()
        client.ping()
        print(f"Building {IMAGE} from {ROOT}")
        image, build_logs = client.images.build(path=str(ROOT), tag=IMAGE, rm=True)
        for item in build_logs:
            if "stream" in item:
                print(item["stream"], end="")
            if "error" in item:
                raise RuntimeError(item["error"])
        print(f"Built image: {image.tags}")

        try:
            client.containers.get(CONTAINER_NAME)
            raise RuntimeError(f"Container name collision: {CONTAINER_NAME} already exists; left untouched")
        except NotFound:
            pass

        try:
            container = client.containers.create(
                image=IMAGE, name=CONTAINER_NAME, detach=True,
                ports={"5000/tcp": None},
                security_opt=[f"apparmor:{PROFILE}"],
                user="app:app",
            )
            created = True
            container.start()
        except APIError as exc:
            raise RuntimeError(
                f"Docker could not create/start with AppArmor profile {PROFILE!r}. "
                "Load and verify it in the daemon's Linux host first. No unconfined fallback was attempted. "
                f"Docker said: {exc}"
            ) from exc

        container.reload()
        requested = container.attrs.get("HostConfig", {}).get("SecurityOpt") or []
        print(f"Requested security options: {requested}")
        if f"apparmor:{PROFILE}" not in requested:
            raise RuntimeError(f"Docker inspect does not show requested profile: {requested}")

        deadline = time.time() + 20
        while time.time() < deadline:
            container.reload()
            if container.status != "running":
                raise RuntimeError(f"Container exited: {container.logs().decode(errors='replace')}")
            code, output = container.exec_run(["cat", "/proc/1/attr/current"])
            effective = output.decode(errors="replace").strip().replace("\x00", "")
            if code == 0:
                break
            time.sleep(0.5)
        else:
            raise RuntimeError("Could not read /proc/1/attr/current to verify the effective profile")
        print(f"Effective profile from PID 1: {effective}")
        if not effective.startswith(PROFILE + " ") and effective != PROFILE:
            raise RuntimeError(f"Expected effective profile {PROFILE!r}; got {effective!r}")

        binding = container.attrs["NetworkSettings"]["Ports"]["5000/tcp"][0]
        url = f"http://127.0.0.1:{binding['HostPort']}/"
        response = requests.get(url, timeout=10)
        print(f"Endpoint {url}: HTTP {response.status_code}; body={response.text!r}")
        if response.status_code != 200 or response.text != EXPECTED:
            raise RuntimeError("Flask endpoint did not return the expected response")
        print("PASS: image built, requested and effective profile verified, endpoint responded")
        return 0
    except (DockerException, RuntimeError, requests.RequestException) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
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

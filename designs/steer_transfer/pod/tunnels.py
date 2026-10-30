"""Open ssh tunnels from this laptop to the pods' vLLM servers and write run/endpoints.json.

  python3 designs/steer_transfer/pod/tunnels.py "Qwen 3.5=st-xfer-a:8000/8101,st-xfer-e:8100/8101" "Qwen 3.8=st-xfer-d:8000,st-xfer-c:8100"

Each listed pod port (one vLLM server per GPU; never 8001, which RunPod's nginx proxies to 8000) it is forwarded to a unique local port (18000, 18001, ...). Uses rp's per-pod
state (~/.runpod-runner/pods/<name>.json) and known_hosts. Tunnels run as background `ssh -N` processes (pids in
run/tunnels.pids); `--close` kills them.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
RP = Path.home() / ".runpod-runner" / "pods"
PIDS = HERE / "run" / "tunnels.pids"


def main():
    if sys.argv[1:] == ["--close"]:
        for pid in PIDS.read_text().split():
            subprocess.run(["kill", pid], check=False)
        PIDS.unlink()
        return
    endpoints, pids, local = {}, [], int(__import__("os").environ.get("LOCAL_BASE", 18000))
    for spec in sys.argv[1:]:
        model, pods = spec.split("=")
        endpoints[model] = []
        for pd in pods.split(","):
            name, ports = pd.split(":")
            st = json.loads((RP / f"{name}.json").read_text())
            fw = []
            for port in ports.split("/"):
                fw += ["-L", f"{local}:localhost:{port}"]
                endpoints[model].append(f"http://localhost:{local}/v1")
                local += 1
            cmd = ["ssh", "-N", "-p", str(st["port"]), "-i", str(Path.home() / ".ssh/id_ed25519"),
                   "-o", f"UserKnownHostsFile={RP / (name + '.known_hosts')}", "-o", "StrictHostKeyChecking=accept-new",
                   "-o", "ServerAliveInterval=30", "-o", "ExitOnForwardFailure=yes", *fw, f"root@{st['ip']}"]
            pids.append(str(subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                             stderr=subprocess.DEVNULL, start_new_session=True).pid))
    time.sleep(3)
    (PIDS.with_name(__import__("os").environ.get("PIDS_FILE", PIDS.name))).write_text(" ".join(pids))
    (HERE / "run" / __import__("os").environ.get("ENDPOINTS_FILE", "endpoints.json")).write_text(json.dumps(endpoints, indent=1))
    print(json.dumps(endpoints, indent=1))


if __name__ == "__main__":
    main()

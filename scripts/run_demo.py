import os
import signal
import shutil
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"


def run_command(command, cwd=None, shell=False):
    print(f"Starting: {' '.join(str(p) for p in command)} in {cwd}")
    return subprocess.Popen([str(p) for p in command], cwd=cwd, shell=shell)


def main():
    print("Seeding sample data...")
    subprocess.run([sys.executable, "scripts/seed_demo.py"], cwd=BACKEND_DIR, check=True)

    print("Generating sample rankings and outputs...")
    subprocess.run([sys.executable, "scripts/generate_sample_rankings.py"], cwd=BACKEND_DIR, check=True)

    print("Starting backend server on http://127.0.0.1:8000...")
    backend_proc = run_command([sys.executable, "manage.py", "runserver", "8000"], cwd=BACKEND_DIR)
    time.sleep(2)

    print("Starting frontend dev server on http://127.0.0.1:4173...")
    npm_executable = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm_executable:
        raise RuntimeError("npm executable not found on PATH")
    frontend_proc = run_command([npm_executable, "run", "dev", "--", "--host", "0.0.0.0", "--port", "4173"], cwd=FRONTEND_DIR)

    print("Demo is running. Open the following URLs:")
    print("- Frontend: http://127.0.0.1:4173")
    print("- Backend API: http://127.0.0.1:8000/api/")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping demo servers...")
        backend_proc.send_signal(signal.SIGINT)
        frontend_proc.send_signal(signal.SIGINT)
        backend_proc.wait()
        frontend_proc.wait()
        print("Demo stopped.")


if __name__ == "__main__":
    import shutil

    main()

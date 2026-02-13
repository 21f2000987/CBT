import os
import sys
import subprocess

def build():
    print("Starting bundling process...")

    # Check for PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Define the PyInstaller command
    # --onefile: bundle into a single executable
    # --add-data: include templates and static files
    # --name: name of the output file

    sep = os.pathsep
    command = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed", # Don't show console on launch
        f"--add-data=app/templates{sep}app/templates",
        f"--add-data=app/static{sep}app/static",
        "--name=CBTEngine",
        "index.py"
    ]

    print(f"Running command: {' '.join(command)}")
    subprocess.check_call(command)
    print("\nBundling complete! The executable is in the 'dist' folder.")

if __name__ == "__main__":
    build()

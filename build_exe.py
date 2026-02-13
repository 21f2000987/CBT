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

    # Define hidden imports for Flask extensions
    hidden_imports = [
        "flask_sqlalchemy",
        "flask_login",
        "flask_bcrypt",
        "flask_wtf",
        "wtforms",
        "email_validator"
    ]

    sep = os.pathsep
    command = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed", # Don't show console on launch
        f"--add-data=app/templates{sep}app/templates",
        f"--add-data=app/static{sep}app/static",
        "--name=CBTEngine",
    ]

    for hi in hidden_imports:
        command.extend(["--hidden-import", hi])

    command.append("index.py")

    print(f"Running command: {' '.join(command)}")
    try:
        subprocess.check_call(command)
        print("\nBundling complete! The executable is in the 'dist' folder.")
    except Exception as e:
        print(f"\nError during bundling: {e}")

if __name__ == "__main__":
    build()

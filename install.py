import sys
import subprocess
import os

def main():
    req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")
    if os.path.isfile(req_file):
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file])
        except Exception as e:
            print(f"Failed to install dependencies: {e}")

if __name__ == "__main__":
    main()